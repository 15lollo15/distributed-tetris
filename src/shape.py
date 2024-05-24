from typing import List


class NotSameSizeException(Exception):
    pass


class Shape:
    def __init__(self, matrix: List[List[bool]]):
        super().__init__()
        self.matrix = matrix
        self.num_rows = len(self.matrix)
        self.num_cols = len(self.matrix[0])

        if self.num_cols != self.num_rows:
            raise NotSameSizeException()

        self.size = self.num_cols
        self.paddings = {
            'top': 0,
            'right': 0,
            'bottom': 0,
            'left': 0
        }
        self.generate_paddings()

    def generate_paddings(self):
        for i_1 in range(self.size):
            i_2 = self.size - i_1 - 1
            if i_1 > i_2:
                break

            find = {'top': False, 'right': False, 'bottom': False, 'left': False}
            for j in range(self.size):
                find['top'] = find['top'] or self.matrix[i_1][j]
                find['bottom'] = find['bottom'] or self.matrix[i_2][j]
                find['left'] = find['left'] or self.matrix[j][i_1]
                find['right'] = find['right'] or self.matrix[j][i_2]

            for pos, found in find.items():
                if not found:
                    self.paddings[pos] += 1

    def __str__(self):
        return str(self.matrix) + '\n' + str(self.paddings)
