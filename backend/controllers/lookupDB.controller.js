const pool = require("../database");

const lookupDBController = {
    showtablas1: async (req, res) => {
        try {
          const sql = `
          SELECT * FROM Formulario
          `;
          const connection = await pool.getConnection();
          const [results, fields] = await connection.query(sql); // Ejecuta la consulta SQL
          connection.release(); // Cierra la conexión después de usarla
          res.json({ msg: results }); // Envía el resultado de la consulta como respuesta JSON
        } catch (error) {
          res.json({ msg: error.message });
        }
      },
      showtablas2: async (req, res) => {
        try {
          const sql = `
          SELECT * FROM Enajenante
          `;
          const connection = await pool.getConnection();
          const [results, fields] = await connection.query(sql); // Ejecuta la consulta SQL
          connection.release(); // Cierra la conexión después de usarla
          res.json({ msg: results }); // Envía el resultado de la consulta como respuesta JSON
        } catch (error) {
          res.json({ msg: error.message });
        }
      },
      showtablas3: async (req, res) => {
        try {
          const sql = `
          SELECT * FROM Adquirente
          `;
          const connection = await pool.getConnection();
          const [results, fields] = await connection.query(sql); // Ejecuta la consulta SQL
          connection.release(); // Cierra la conexión después de usarla
          res.json({ msg: results }); // Envía el resultado de la consulta como respuesta JSON
        } catch (error) {
          res.json({ msg: error.message });
        }
      },
      showtablas4: async (req, res) => {
        try {
          const sql = `
          SELECT * FROM Multipropietario
          `;
          const connection = await pool.getConnection();
          const [results, fields] = await connection.query(sql); // Ejecuta la consulta SQL
          await connection.release(); // Cierra la conexión después de usarla
          res.json({ msg: results }); // Envía el resultado de la consulta como respuesta JSON
        } catch (error) {
          res.json({ msg: error.message });
        }
      },
};

module.exports = lookupDBController;