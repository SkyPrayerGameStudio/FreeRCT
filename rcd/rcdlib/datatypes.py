# $Id$
#
# This file is part of FreeRCT.
# FreeRCT is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 2.
# FreeRCT is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with FreeRCT. If not, see <http://www.gnu.org/licenses/>.
#

class DataType(object):
    """
    Data type of a field.

    @ivar name: Name of the data type.
    @type name: C{unicode}
    """
    def __init__(self, name):
        self.name = name

    def get_size(self):
        """
        Retrieve the size of the data type.

        @return: Size of the data type in the RCD file (in bytes).
        @rtype:  C{int}
        """
        raise NotImplementedError("Implement me in %r" % type(self))

    def write(self, out, value):
        """
        Write the value onto the output.

        @param out: Output stream.
        @type  out: L{Output}

        @param value: Value to write.
        @type  value: Varies with each type
        """
        raise NotImplementedError("Implement me in %r" % type(self))


class NumericDataType(DataType):
    """
    Simple numeric data type.
    """
    SIZES = {'int8': 1, 'uint8': 1, 'int16': 2, 'uint16': 2, 'int32': 4, 'uint32': 4,}
    _writer = {  'int8' : lambda out, value: out.int8(value),
                'uint8' : lambda out, value: out.uint8(value),
                 'int16': lambda out, value: out.int16(value),
                'uint16': lambda out, value: out.uint16(value),
                'uint32': lambda out, value: out.uint32(value), }

    def __init__(self, name):
        DataType.__init__(self, name)

    def get_size(self, value):
        return self.SIZES[self.name]

    def write(self, out, value):
        self._writer[self.name](out, value)


class BlockReference(DataType):
    """
    Data type of a block reference.
    """
    def __init__(self, name):
        DataType.__init__(self, name)

    def get_size(self, value):
        return 4

    def write(self, out, value):
        if value is None:
            value = 0
        out.uint32(value)


class ImageDataType(DataType):
    """
    Data type of image data.
    """
    def __init__(self):
        DataType.__init__(self, 'image_data')

    def get_size(self, line_data):
        """
        Compute the size (in bytes) for the pixel data.

        @param line_data: Data of each line, C{None} means the line is empty.
        @type  line_data: C{list} of (C{str} or C{None})

        @return: The size of the data field in the rcd file.
        @rtype:  C{int}
        """
        total = 0
        for line in line_data:
            total = total + 4
            if line is not None:
                total = total + len(line)
        return total

    def write(self, out, line_data):
        """
        Write the image data.

        @param out: Output stream.
        @type  out: L{Output}

        @param line_data: Data of each line, C{None} means the line is empty.
        @type  line_data: C{list} of (C{str} or C{None})
        """
        offset = 4 * len(line_data)
        for line in line_data:
            if line is not None:
                out.uint32(offset)
                offset = offset + len(line)
            else:
                out.uint32(0)
        for line in line_data:
            if line is not None:
                out.store_text(line)



UINT8_TYPE  = NumericDataType('uint8')
INT8_TYPE   = NumericDataType('int8')
UINT16_TYPE = NumericDataType('uint16')
INT16_TYPE  = NumericDataType('int16')
UINT32_TYPE = NumericDataType('uint32')
INT32_TYPE  = NumericDataType('int32')
SPRITE_TYPE = BlockReference('sprite')
BLOCK_TYPE  = BlockReference('block')
IMAGE_DATA_TYPE = ImageDataType()


class DataTypeFactory(object):
    """
    Factory class for data types.

    @ivar types: Available data types ordered by name.
    @type types: C{dict} of C{unicode} to L{DataType}
    """
    def __init__(self):
        self.types = None

    def init_types(self):
        self.types = {}
        self.add_type( UINT8_TYPE)
        self.add_type(  INT8_TYPE)
        self.add_type(UINT16_TYPE)
        self.add_type( INT16_TYPE)
        self.add_type(UINT32_TYPE)
        self.add_type( INT32_TYPE)
        self.add_type(SPRITE_TYPE)
        self.add_type(BLOCK_TYPE)
        self.add_type(IMAGE_DATA_TYPE)

    def add_type(self, dt):
        """
        Add a new data type.

        @param dt: Data type to add.
        @type  dt: C{DataType}
        """
        if self.types is None:
            self.init_types()

        assert dt.name not in self.types
        self.types[dt.name] = dt



    def get_type(self, name):
        """
        Get a data type by name.

        @param name: Name of the data type to retrieve.
        @type  name: C{unicode}

        @return: The requested data type.
        @rtype:  C{DataType}
        """
        if self.types is None:
            self.init_types()

        return self.types[name]

factory = DataTypeFactory()

