const pool = require("../database");

const executeQuery2 = async (sql, parameters) => {
  try {
    const connection = await pool.getConnection();
    const [results, fields] = await connection.query(sql, parameters = []);
    connection.release();
    return results
  } catch (error) {
    console.error(error.message);
    return null;
  }
};

const lookupDBController2 = {
  EnajenanteTables: async (req, res) => {
    const sql = `SELECT * FROM Enajenante`;
    res.body = await executeQuery2(sql);
  },
  AdquirienteTables: async (req, res) => {
    const sql = `SELECT * FROM Adquirente`;
    res.body = await executeQuery2(sql);
  },
  FormularioTables: async (req, res) => {
    const sql = `SELECT * FROM Formulario`;
    res.body = await executeQuery2(sql);
  },
  FormularioCMP: async (req, res) => {
    const sql = `SELECT * FROM Formulario WHERE comuna = ? AND manzana = ? AND predio = ?`;
    const { comuna, manzana, predio } = req.body;
    res.body = await executeQuery2(sql, [comuna, manzana, predio]);
  },
  MultipropietrioTables: async (req, res) => {
    const sql = `SELECT * FROM Multipropietario`;
    res.body = await executeQuery2(sql);
  },
  MultipropietrioCMP: async (req, res) => {
    const sql = `SELECT * FROM Multipropietario WHERE comuna = ? AND manzana = ? AND predio = ?`;
    const { comuna, manzana, predio } = req.body;
    res.body = await executeQuery2(sql, [comuna, manzana, predio]);
  },
};

module.exports = lookupDBController2;
