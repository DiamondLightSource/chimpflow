"""
Script to detect positions of crystals in a folder of drop images using Mask-R-CNN based object detector.
"""
import logging
from pathlib import Path
from typing import Dict

from dls_utilpack.describe import describe
from dls_utilpack.require import require
from xchem_chimp.detector.chimp_detector import ChimpDetector
from xchem_chimp.detector.coord_generator import ChimpXtalCoordGenerator, PointsMode
from xchembku_api.models.well_geometry_model import WellGeometryModel
from xchembku_api.models.well_model import WellModel

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
        self.__specification = specification

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

    async def process(self, well_model: WellModel) -> WellGeometryModel:
        """
        Process the input well and produce results.

        Args:
            well (Dict): _description_

        Returns:
            Dict: _description_
        """

        # Filename is full path to where images are saved.
        filename: Path = Path(well_model.filename)

        detector = ChimpDetector(
            self.__model_path,
            [str(filename)],
            self.__num_classes,
        )

        coord_generator = ChimpXtalCoordGenerator(
            detector, points_mode=PointsMode.SINGLE, extract_echo=False
        )
        coord_generator.extract_coordinates()
        coord_generator.calculate_well_centres()

        output_dict = coord_generator.combined_coords_list[0]
        logger.debug(describe("output_dict", output_dict))

        model = WellGeometryModel(well_uuid=well_model.uuid)
        model.drop_detected = output_dict["drop_detected"]
        target_position = output_dict["echo_coordinate"]
        if len(target_position) > 0:
            model.target_position_x, model.target_position_y = target_position[0]
        well_centroid = output_dict["well_centroid"]
        model.well_centroid_x, model.well_centroid_y = well_centroid
        model.number_of_crystals = len(output_dict["xtal_coordinates"])
        model.crystal_coordinates = output_dict["xtal_coordinates"]

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

        return model
