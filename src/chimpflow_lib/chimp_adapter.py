import logging
import warnings
from pathlib import Path
from typing import Dict

from dls_utilpack.describe import describe
from dls_utilpack.require import require
from xchem_chimp.detector.coord_generator import ChimpXtalCoordGenerator, PointsMode
from xchembku_api.models.crystal_well_autolocation_model import (
    CrystalWellAutolocationModel,
)
from xchembku_api.models.crystal_well_model import CrystalWellModel

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from xchem_chimp.detector.chimp_detector import ChimpDetector


logger = logging.getLogger(__name__)


class ChimpAdapter:
    """
    Class to adapt data results from chimp to concept of "well_locations" object as known to xchembku.
    """

    def __init__(self, specification: Dict):
        """
        Constructor

        Args:
            specification (Dict): arguments to the adapter

        Keywords:
            model_path: filename of the pytorch file
            num_classes: input to chimp detect, normally always 3
        """

        self.__model_path = require(
            "specification",
            specification,
            "model_path",
        )
        self.__num_classes = require(
            "specification",
            specification,
            "num_classes",
        )

    def detect(
        self, crystal_well_model: CrystalWellModel
    ) -> CrystalWellAutolocationModel:
        """
        Process the input well and produce results.

        Args:
            crystal_well_model (CrystalWellModel): The crystal well model to process for locations.

        Returns:
            CrystalWellAutolocationModel: The autolocation data mined from the image for the crystal well.
        """

        # Filename is full path to the input filename.
        filename: Path = Path(crystal_well_model.filename)

        if not filename.exists():
            raise RuntimeError(f"could not find file {str(filename)}")

        # Make a detector object.
        # TODO: Arrange ChimpDetector internals so that we only have to load
        # the torch model once per server, instead of once per detection request.
        detector = ChimpDetector(
            self.__model_path,
            [str(filename)],
            self.__num_classes,
        )

        # Create a coordiate generator object.
        coord_generator = ChimpXtalCoordGenerator(
            detector, points_mode=PointsMode.SINGLE, extract_echo=True
        )

        # Extract the crystal coordinates.
        coord_generator.extract_coordinates()

        # Calculate well centers.
        coord_generator.calculate_well_centres()
        output_dict = coord_generator.combined_coords_list[0]

        logger.debug(describe("output_dict", output_dict))

        # Construct a new autolocation object to hold the results.
        model = CrystalWellAutolocationModel(
            crystal_well_uuid=crystal_well_model.uuid,
        )
        model.drop_detected = output_dict["drop_detected"]
        target_position = output_dict["echo_coordinate"]
        if len(target_position) > 0:
            # The target position is a list of (np.int64, np.int64), so have to convert to int.
            # TODO: Change the CrystalWellAutolocationModel to do type checking on field assignment.
            model.auto_target_x = int(target_position[0][0])
            model.auto_target_y = int(target_position[0][1])
        well_centroid = output_dict["well_centroid"]
        if well_centroid is not None:
            model.well_centroid_x = int(well_centroid[0])
            model.well_centroid_y = int(well_centroid[1])
        model.number_of_crystals = len(output_dict["xtal_coordinates"])

        # TODO: Store the chimp detected crystal coordinates in the model too.
        # model.crystal_coordinates = list(output_dict["xtal_coordinates"])

        # request_dict[ImageFieldnames.FILENAME] = str(im_path)
        # if output_dict["drop_detected"] is True:
        #     request_dict[ImageFieldnames.IS_DROP] = True
        #     echo_y, echo_x = output_dict["echo_coordinate"][0]
        #     request_dict[ImageFieldnames.TARGET_POSITION_Y] = int(echo_y)
        #     request_dict[ImageFieldnames.TARGET_POSITION_X] = int(echo_x)
        #     centroid_y, centroid_x = output_dict["well_centroid"]
        #     request_dict[ImageFieldnames.WELL_CENTER_Y] = int(centroid_y)
        #     request_dict[ImageFieldnames.WELL_CENTER_X] = int(centroid_x)
        #     num_xtals = len(output_dict["xtal_coordinates"])
        #     request_dict[ImageFieldnames.NUMBER_OF_CRYSTALS] = int(num_xtals)
        #     logging.info(f"output_dict is\n{describe('output_dict', output_dict)}")
        # else:
        #     request_dict[ImageFieldnames.IS_DROP] = False
        #     request_dict[ImageFieldnames.IS_USABLE] = False
        # logging.info(f"Sending request for {im_path} to EchoLocator database")
        # asyncio.run(self.send_item_to_echolocator(request_dict))

        # import numpy as np
        # import json

        # class NumpyEncoder(json.JSONEncoder):
        #     def default(self, obj):
        #         if isinstance(obj, np.ndarray):
        #             return obj.tolist()
        #         if isinstance(obj, np.int64):
        #             return int(obj)
        #         return json.JSONEncoder.default(self, obj)

        #         logging.info(
        #             f"extracted coordinates\n{json.dumps(coord_generator.combined_coords_list, indent=4, cls=NumpyEncoder)}"
        #         )

        # The combined_coords_list is structured like this:
        # [
        #     {
        #         "image_path": "tests/echo_test_imgs/echo_test_im_3.jpg",
        #         "mask_index": [
        #             0,
        #             1,
        #             2
        #         ],
        #         "masks": [],
        #         "probs": [],
        #         "labels": [
        #             1,
        #             2,
        #             2,
        #             1,
        #             2,
        #             2,
        #             2
        #         ],
        #         "bounding_boxes": [],
        #         "xtal_coordinates": [
        #             [
        #                 [
        #                     552,
        #                     616
        #                 ]
        #             ],
        #             [
        #                 [
        #                     598,
        #                     840
        #                 ]
        #             ]
        #         ],
        #         "well_centroid": [
        #             504,
        #             608
        #         ],
        #         "echo_coordinate": [
        #             [
        #                 419,
        #                 764
        #             ]
        #         ],
        #         "real_space_offset": [
        #             -241.0,
        #             443.0
        #         ],
        #         "original_image_shape": [
        #             1024,
        #             1224
        #         ],
        #         "drop_detected": true
        #     }
        # ]

        return model
