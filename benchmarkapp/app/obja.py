#!/usr/bin/env python3

import sys

SIZES = {"v": 13, "f": 4, "ev": 14, "tv": 14, "ef": 5, "efv": 4, "df": 1, "ts": 6, "tf": 7, "s": 0, "#": 0, "fc": 0}

"""
obja model for python.
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

    def translate(self, array):
        """
        Translates a vector from an array of string representing floats.
        """
        self.x += float(array[0])
        self.y += float(array[1])
        self.z += float(array[2])

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

    def test(self, vertices, line=-1):
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
        Initializes an empty model.
        """
        self.vertices = []
        self.faces = []
        self.line = 0
        self.steps = []
        self.vertex_steps = []
        self.faces_steps = []
        self.steps_temp = []
        self.model_steps = []
        self.vertex_steps_temp = []
        self.faces_steps_temp = []
        self.faces_color = []
        self.size = 0
        self.declared_size = 0
        self.file_len = 0

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
            f = file.readlines()
            self.file_len = len(f)
            for line in f:
                self.parse_line(line)
        if self.steps:
            self.steps = [s / self.steps[-1] for s in self.steps]
        else:
            self.steps = [s / self.steps_temp[-1] for s in self.steps_temp]
            self.faces_steps = self.faces_steps_temp
            self.vertex_steps = self.vertex_steps_temp

    def parse_line(self, line):
        """
        Parses a line of obja file.
        """
        self.line += 1

        split = line.split()

        if len(split) == 0:
            return

        self.size += SIZES[split[0]]

        if split[0] == "v":
            self.vertices.append(Vector.from_array(split[1:]))

        elif split[0] == "ev":
            self.get_vector_from_string(split[1]).set(split[2:])

        elif split[0] == "tv":
            self.get_vector_from_string(split[1]).translate(split[2:])

        elif split[0] == "f" or split[0] == "tf":
            for i in range(1, len(split) - 2):
                face = Face(split[i:i + 3])
                print(f"Face : {face}")
                face.test(self.vertices, self.line)
                self.faces.append(face)
                # self.faces_color.append([1.0,1.0,1.0])

        elif split[0] == "ts":
            for i in range(1, len(split) - 2):
                if i % 2 == 1:
                    face = Face([split[i], split[i + 1], split[i + 2]])
                else:
                    face = Face([split[i], split[i + 2], split[i + 1]])
                face.test(self.vertices, self.line)
                self.faces.append(face)

        elif split[0] == "ef":
            self.get_face_from_string(split[1]).set(split[2:])

        elif split[0] == "efv":
            face = self.get_face_from_string(split[1])
            vector = int(split[2])
            new_index = int(split[3]) - 1
            if vector == 1:
                face.a = new_index
            elif vector == 2:
                face.b = new_index
            elif vector == 3:
                face.c = new_index
            else:
                raise FaceVertexError(vector, self.line)

        elif split[0] == "df":
            self.get_face_from_string(split[1]).visible = False

        elif split[0] == "s":
            vert_list, faces_list = self.get_lists()
            self.steps.append(int(split[1]))
            self.model_steps.append(self)
            self.vertex_steps.append(vert_list)
            self.faces_steps.append(faces_list)
            self.declared_size = int(split[1])

        elif split[0] == "fc":
            # self.faces_color[int(split[1])] = [float(split[2]),float(split[3]),float(split[4])]
            return

        elif split[0] == "#":
            return

        else:
            return
            # raise UnknownInstruction(split[0], self.line)
        if not self.line % (self.file_len // 10) and not self.steps:
            vert_list, faces_list = self.get_lists()
            self.steps_temp.append(self.line)
            self.vertex_steps_temp.append(vert_list)
            self.faces_steps_temp.append(faces_list)

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
        print("obja needs a path to an obja file")
        return

    model = parse_file(sys.argv[1])
    print(model.vertices)
    print(model.faces)


if __name__ == "__main__":
    main()
