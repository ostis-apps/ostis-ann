import numpy

from .Converter import Converter
from modules.UseProblemSolvingMethodModule.dataClasses.inputOutput.ImageStruct import Image


class ImageConverter(Converter):
    @staticmethod
    def convert_image_to_inputs(image: Image, number_of_inputs: int) -> numpy.array:
        numpydata = image.data_array
        numpy.shape(numpydata)

        numpydata = numpy.reshape(numpydata, (1, number_of_inputs))
        return numpydata
