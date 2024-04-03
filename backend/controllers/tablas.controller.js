const mysql = require("mysql2/promise");
const connection = require("../database");

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
      const connection = await mysql.createConnection({
        host: "flask-g19-miuandes-3b9d.a.aivencloud.com",
        user: "avnadmin",
        password: "AVNS_LHyyUux2JxRT64CsmA5",
        database: "defaultdb",
        port: 18573,
      });
      await connection.query(sql);
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
      const connection = await mysql.createConnection({
        host: "flask-g19-miuandes-3b9d.a.aivencloud.com",
        user: "avnadmin",
        password: "AVNS_LHyyUux2JxRT64CsmA5",
        database: "defaultdb",
        port: 18573,
      });
      await connection.query(sql);
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
      const connection = await mysql.createConnection({
        host: "flask-g19-miuandes-3b9d.a.aivencloud.com",
        user: "avnadmin",
        password: "AVNS_LHyyUux2JxRT64CsmA5",
        database: "defaultdb",
        port: 18573,
      });
      await connection.query(sql);
      res.json({ msg: "Tabla 'Adquirente' creada correctamente" });
    } catch (error) {
      res.json({ msg: error.message });
    }
  },
  showtablas: async (req, res) => {
    try {
      const sql = `
      SELECT * FROM Formulario
      `;
      const connection = await mysql.createConnection({
        host: "flask-g19-miuandes-3b9d.a.aivencloud.com",
        user: "avnadmin",
        password: "AVNS_LHyyUux2JxRT64CsmA5",
        database: "defaultdb",
        port: 18573,
      });
      const [results, fields] = await connection.query(sql); // Ejecuta la consulta SQL
      await connection.end(); // Cierra la conexión después de usarla
      res.json({ msg: results }); // Envía el resultado de la consulta como respuesta JSON
    } catch (error) {
      res.json({ msg: error.message });
    }
  },
};

module.exports = tablasController;
