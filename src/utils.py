from typing import List


def rotate_matrix(matrix: List[List[bool]]) -> List[List[bool]]:
    width = len(matrix)
    height = len(matrix[0])
    r_matrix = [[False for _ in range(width)] for _ in range(height)]
    for i in range(height):
        for j in range(width):
            r_matrix[i][j] = matrix[width - j - 1][i]
    return r_matrix


def generate_rotations(matrix: List[List[bool]]) -> List[List[List[bool]]]:
    rotations = [matrix.copy()]
    for _ in range(3):
        r_matrix = rotate_matrix(rotations[len(rotations) - 1])
        rotations.append(r_matrix)
    return rotations
