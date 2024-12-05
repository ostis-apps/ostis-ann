from PIL import Image
import numpy


class Converter:
    def convert(image_path) -> numpy.array:
        image = Image.open(image_path)
        numpydata = numpy.array(image)
        numpy.shape(numpydata)
        numpydata[numpydata < 0.5] = 0
        numpydata[numpydata >= 0.5] = 1
        numpydata = numpy.reshape(numpydata, (1,784))
        return numpydata
    
    
