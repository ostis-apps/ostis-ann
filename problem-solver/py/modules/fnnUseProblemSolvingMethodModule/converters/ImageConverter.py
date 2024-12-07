import numpy

from modules.fnnUseProblemSolvingMethodModule.converters import Converter
from modules.fnnUseProblemSolvingMethodModule.dataClasses.inputOutput.ImageStruct import Image


class ImageConverter(Converter):
    def convert_image_to_inputs(image:Image, number_of_inputs:int) -> numpy.array:
        numpydata = image.image_array
        numpy.shape(numpydata)

        numpydata = numpy.reshape(numpydata, (1, number_of_inputs))
        return numpydata