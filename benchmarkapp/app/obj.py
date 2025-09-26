#!/usr/bin/env python3

import sys

"""
obj model for python.
"""


class Vector:
    """
    The class that holds the x, y, and z coordinates of a vector.
    """

    def __init__(self, x, y, z):
        """
        Initializes a vector from values.
        """
        self.x = x
        self.y = y
        self.z = z

    def from_array(array):
        """
        Creates a vector from an array of string representing floats.
        """
        return Vector(0, 0, 0).set(array)

    def set(self, array):
        """
        Sets a vector from an array of string representing floats.
        """
        self.x = float(array[0])
        self.y = float(array[1])
        self.z = float(array[2])
        return self

    def __str__(self):
        return "({}, {}, {})".format(self.x, self.y, self.z)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        return Vector(self.x * other, self.y * other, self.z * other)

    def __truediv__(self, other):
        return Vector(self.x / other, self.y / other, self.z / other)

    def __repr__(self):
        return str(self)


class Face:
    """
    The class that holds a, b, and c, the indices of the vertices of the face.
    """

    def __init__(self, array):
        """
        Initializes a face from an array of strings representing vector indices (starting at 1)
        """
        self.set(array)
        self.visible = True

    def set(self, array):
        """
        Sets a face from an array of strings representing vector indices (starting at 1)
        """
        self.a = int(array[0].split('/')[0]) - 1
        self.b = int(array[1].split('/')[0]) - 1
        self.c = int(array[2].split('/')[0]) - 1
        return self

    def test(self, vertices, line="unknown"):
        """
        Tests if a face references only vertices that exist when the face is declared.
        """
        if self.a >= len(vertices):
            raise VertexError(self.a + 1, line)
        if self.b >= len(vertices):
            raise VertexError(self.b + 1, line)
        if self.c >= len(vertices):
            raise VertexError(self.c + 1, line)

    def __str__(self):
        return "Face({}, {}, {})".format(self.a, self.b, self.c)

    def __repr__(self):
        return str(self)


class VertexError(Exception):
    """
    An operation references a vertex that does not exist.
    """

    def __init__(self, index, line):
        """
        Creates the error from index of the referenced vertex and the line where the error occured.
        """
        self.line = line
        self.index = index
        super().__init__()

    def __str__(self):
        """
        Pretty prints the error.
        """
        return f'There is no vector {self.index} (line {self.line})'


class FaceError(Exception):
    """
    An operation references a face that does not exist.
    """

    def __init__(self, index, line):
        """
        Creates the error from index of the referenced face and the line where the error occured.
        """
        self.line = line
        self.index = index
        super().__init__()

    def __str__(self):
        """
        Pretty prints the error.
        """
        return f'There is no face {self.index} (line {self.line})'


class FaceVertexError(Exception):
    """
    An operation references a face vector that does not exist.
    """

    def __init__(self, index, line):
        """
        Creates the error from index of the referenced face vector and the line where the error occured.
        """
        self.line = line
        self.index = index
        super().__init__()

    def __str__(self):
        """
        Pretty prints the error.
        """
        return f'Face has no vector {self.index} (line {self.line})'


class UnknownInstruction(Exception):
    """
    An instruction is unknown.
    """

    def __init__(self, instruction, line):
        """
        Creates the error from instruction and the line where the error occured.
        """
        self.line = line
        self.instruction = instruction
        super().__init__()

    def __str__(self):
        """
        Pretty prints the error.
        """
        return f'Instruction {self.instruction} unknown (line {self.line})'


class Model:
    """
    The OBJA model.
    """

    def __init__(self):
        """
        Intializes an empty model.
        """
        self.vertices = []
        self.faces = []
        self.line = 0

    def get_vector_from_string(self, string):
        """
        Gets a vector from a string representing the index of the vector, starting at 1.
        To get the vector from its index, simply use model.vertices[i].
        """
        index = int(string) - 1
        if index >= len(self.vertices):
            raise FaceError(index + 1, self.line)
        return self.vertices[index]

    def get_face_from_string(self, string):
        """
        Gets a face from a string representing the index of the face, starting at 1.
        To get the face from its index, simply use model.faces[i].
        """
        index = int(string) - 1
        if index >= len(self.faces):
            raise FaceError(index + 1, self.line)
        return self.faces[index]

    def parse_file(self, path):
        """
        Parses an OBJA file.
        """
        with open(path, "r") as file:
            for line in file.readlines():
                self.parse_line(line)

    def parse_line(self, line):
        """
        Parses a line of obja file.
        """
        self.line += 1

        split = line.split()

        if len(split) == 0:
            return

        if split[0] == "v":
            self.vertices.append(Vector.from_array(split[1:]))

        elif split[0] == "f":
            for i in range(1, len(split) - 2):
                face = Face(split[i:i + 3])
                face.test(self.vertices, self.line)
                self.faces.append(face)

        elif split[0] == "ts":
            for i in range(1, len(split) - 2):
                if i % 2 == 1:
                    face = Face([split[i], split[i + 1], split[i + 2]])
                else:
                    face = Face([split[i], split[i + 2], split[i + 1]])
                face.test(self.vertices, self.line)
                self.faces.append(face)

        elif split[0] == "#":
            return

        else:
            return
            # raise UnknownInstruction(split[0], self.line)

    def get_lists(self):
        vert_list = []
        faces_list = []
        for vert in self.vertices:
            vert_list.append(tuple([vert.x, vert.y, vert.z]))
        for face in self.faces:
            faces_list.append(tuple([face.a, face.b, face.c]))
        return vert_list, faces_list


def parse_file(path):
    """
    Parses a file and returns the model.
    """
    model = Model()
    model.parse_file(path)
    return model


def main():
    if len(sys.argv) == 1:
        print("obj needs a path to an obj file")
        return

    model = parse_file(sys.argv[1])
    print(model.vertices)
    print(model.faces)


if __name__ == "__main__":
    main()
