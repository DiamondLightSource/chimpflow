"""
Script to detect positions of crystals in a folder of drop images using Mask-R-CNN based object detector.
"""
from typing import Dict

from dls_utilpack.require import require
from xchem_chimp.detector.chimp_detector import ChimpDetector
from xchem_chimp.detector.coord_generator import ChimpXtalCoordGenerator, PointsMode
from xchem_chimp.detector.mask_saver import ChimpXtalMaskSaver


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

    async def process(self, well: Dict) -> Dict:
        """
        Process the input well and produce results.

        Args:
            well (Dict): _description_

        Returns:
            Dict: _description_
        """

        # Filename is full path to where images are saved.
        filename: str = require("well", well, "filename")

        # Directory output selected for this chimp run.
        output_directory: str = require("well", well, "output_directory")

        detector = ChimpDetector(
            self.__model_path,
            [filename],
            self.__num_classes,
        )

        coord_generator = ChimpXtalCoordGenerator(
            detector, points_mode=PointsMode.SINGLE, extract_echo=False
        )
        coord_generator.extract_coordinates()
        coord_generator.calculate_well_centres()
        coord_generator.save_preview_images(output_directory)

        mask_saver = ChimpXtalMaskSaver(detector, output_directory)
        mask_saver.extract_masks()

        return {}
