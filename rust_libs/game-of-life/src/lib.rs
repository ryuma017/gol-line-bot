//! Rules (https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life)
//! 1. Any live cell with fewer than two live neighbours dies, as if by underpopulation.
//! 2. Any live cell with two or three live neighbours lives on to the next generation.
//! 3. Any live cell with more than three live neighbours dies, as if by overpopulation.
//! 4. Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
//!
//! 隣接する生存している cell の数を n とする.
//!
//! | current state |     n     | next state |      description      |
//! | ------------- | --------- | ---------- | --------------------- |
//! | Alive         | n < 2     | Dead       | underpopulation (過疎) |
//! | Alive         | 2 ≤ n ≤ 3 | Alive      | keep alive (生存)      |
//! | Alive         | 3 < n     | Dead       | overpopulation (過密)  |
//! | Dead          | n = 3     | Alive      | reproduction (誕生)    |

use pyo3::{
    exceptions::PyValueError, pyclass, pymethods, pymodule, types::PyModule, PyErr, PyResult,
    Python, wrap_pyfunction, pyfunction,
};

#[pymodule]
fn game_of_life(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Field>()?;
    m.add_function(wrap_pyfunction!(get_status, m)?)?;
    Ok(())
}

#[pyclass]
struct Field {
    #[pyo3(get)]
    width: usize,
    #[pyo3(get)]
    height: usize,
    cells: Vec<CellState>,
    // TODO
    // is_frozen: bool,
}

#[pymethods] // public
impl Field {
    // FIXME: error handling
    #[new]
    fn new(width: usize, height: usize, cells: Vec<usize>) -> Result<Field, PyErr> {
        if width * height != cells.len() {
            return Err(PyValueError::new_err("Invalid cells length"));
        }
        let cells = cells
            .iter()
            .map(|i| match i {
                0 => Some(CellState::Dead),
                1 => Some(CellState::Alive),
                _ => None,
            })
            .collect::<Vec<Option<CellState>>>();
        if cells.iter().any(|i| i.is_none()) {
            return Err(PyValueError::new_err("Invalid cell state"));
        }
        Ok(Field {
            width,
            height,
            cells: cells.iter().map(|i| i.unwrap()).collect(),
        })
    }

    // FIXME: flozen field か判定
    // | current state |     n     | next state |      description      |
    // | ------------- | --------- | ---------- | --------------------- |
    // | Alive         | n < 2     | Dead       | underpopulation (過疎) |
    // | Alive         | 2 ≤ n ≤ 3 | Alive      | keep alive (生存)      |
    // | Alive         | 0 < n     | Dead       | overpopulation (過密)  |
    // | Dead          | n = 3     | Alive      | reproduction (誕生)    |
    fn next(&mut self) {
        let mut next = self.cells.clone();

        for row in 0..self.height {
            for column in 0..self.width {
                let idx = self.get_index(row, column);
                let cell = self.cells[idx];
                let live_neighbors = self.live_neighbor_count(row, column);

                let next_cell = match (cell, live_neighbors) {
                    // 誕生
                    (CellState::Dead, 3) => CellState::Alive,
                    // 生存
                    (CellState::Alive, 2) | (CellState::Alive, 3) => CellState::Alive,
                    // 過疎 or 過密
                    (CellState::Alive, _) | (CellState::Dead, _) => CellState::Dead,
                };
                next[idx] = next_cell;
            }
        }
        self.cells = next;
    }

    fn drow(&self) -> String {
        self.to_string()
    }

    fn drow_as_2d_bit_array(&self) -> Vec<Vec<u8>> {
        let mut result = Vec::new();
        for line in self.cells.as_slice().chunks(self.width as usize) {
            let mut inner = Vec::new();
            for &cell in line.iter() {
                match cell {
                    CellState::Alive => inner.push(1),
                    CellState::Dead => inner.push(0),
                }
            }
            result.push(inner);
        }
        result
    }
}

// private methods
impl Field {
    fn get_index(&self, row: usize, column: usize) -> usize {
        row * self.width + column
    }

    fn live_neighbor_count(&self, row: usize, column: usize) -> u8 {
        let mut count = 0;
        for delta_row in [self.height - 1, 0, 1].into_iter() {
            for delta_col in [self.width - 1, 0, 1].into_iter() {
                // オーバーフロー(アンダーフロー?) 防止
                if delta_row == 0 && delta_col == 0 {
                    continue;
                }

                let neighbor_row = (row + delta_row) % self.height;
                let neighbor_col = (column + delta_col) % self.width;
                let idx = self.get_index(neighbor_row, neighbor_col);
                count += self.cells[idx] as u8;
            }
        }
        count
    }
}

impl std::fmt::Display for Field {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        for line in self.cells.as_slice().chunks(self.width as usize) {
            for (i, &cell) in line.iter().enumerate() {
                if i == self.width - 1 {
                    write!(f, "{}", cell)?;
                } else {
                    write!(f, "{} ", cell)?;
                }
            }
            writeln!(f)?;
        }

        Ok(())
    }
}

#[derive(Clone, Copy)]
enum CellState {
    Dead,
    Alive,
}

impl std::fmt::Display for CellState {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            CellState::Dead => write!(f, "□"),
            CellState::Alive => write!(f, "■"),
        }
    }
}

#[pyfunction]
fn get_status(field: &mut Field, frame_n: u8) -> Vec<Vec<Vec<u8>>> {
    let mut status = Vec::new();
    for _ in 0..frame_n {
        field.next();
        status.push(field.drow_as_2d_bit_array());
    }
    status
}

#[cfg(test)]
mod tests {
    use super::*;

    fn gen_3x3_fields(cells_vec: Vec<Vec<usize>>) -> Vec<Field> {
        let mut fields = Vec::new();
        for cells in cells_vec {
            let field = Field::new(3, 3, cells).unwrap();
            fields.push(field);
        }
        fields
    }

    #[test]
    fn any_live_cell_with_fewer_than_two_live_neighbours_dies() {
        // Arrange
        let cells_vec = vec![
            vec![0, 0, 0, 1, 1, 0, 0, 0, 0],
            vec![0, 1, 0, 0, 1, 0, 0, 0, 0],
            vec![1, 0, 0, 0, 1, 0, 0, 0, 0],
            vec![0, 0, 0, 0, 1, 0, 0, 0, 1],
        ];
        let fields = gen_3x3_fields(cells_vec);
    }
}
