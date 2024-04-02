const mysql = require("../database");

const tablasController = {
  createFormularioTable: async (req, res) => {
    try {
      const sql = `
        CREATE TABLE IF NOT EXISTS Formulario (
          id INT AUTO_INCREMENT PRIMARY KEY,
          numero_atencion VARCHAR(255),
          cne INT,
          comuna INT,
          manzana INT,
          predio INT,
          fojas INT,
          fecha_inscripcion DATE,
          numero_inscripcion VARCHAR(255)
        )
      `;
      await mysql.query(sql);
      res.json({ msg: "Tabla 'Formulario' creada correctamente" });
    } catch (error) {
      res.json({ msg: error.message });
    }
  },

  createEnajenanteTable: async (req, res) => {
    try {
      const sql = `
        CREATE TABLE IF NOT EXISTS Enajenante (
          id INT AUTO_INCREMENT PRIMARY KEY,
          runrut VARCHAR(255),
          porc_derecho FLOAT,
          formulario_id INT,
          FOREIGN KEY (formulario_id) REFERENCES Formulario(id)
        )
      `;
      await mysql.query(sql);
      res.json({ msg: "Tabla 'Enajenante' creada correctamente" });
    } catch (error) {
      res.json({ msg: error.message });
    }
  },

  createAdquirenteTable: async (req, res) => {
    try {
      const sql = `
        CREATE TABLE IF NOT EXISTS Adquirente (
          id INT AUTO_INCREMENT PRIMARY KEY,
          runrut_adq VARCHAR(255),
          porc_derecho_adq FLOAT,
          formulario_id INT,
          FOREIGN KEY (formulario_id) REFERENCES Formulario(id)
        )
      `;
      await mysql.query(sql);
      res.json({ msg: "Tabla 'Adquirente' creada correctamente" });
    } catch (error) {
      res.json({ msg: error.message });
    }
  },
};

module.exports = tablasController;
