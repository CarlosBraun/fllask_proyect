const pool = require("../database");

const executeQuery2 = async (sql, parameters = []) => {
  try {
    const connection = await pool.getConnection();
    const [results, fields] = await connection.query(sql, parameters);
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
    const body = await executeQuery2(sql);
    res.json({ body });
  },
  AdquirienteTables: async (req, res) => {
    const sql = `SELECT * FROM Adquirente`;
    const body = await executeQuery2(sql);
    res.json({ body });
  },
  FormularioTables: async (req, res) => {
    const sql = `SELECT * FROM Formulario`;
    const body = await executeQuery2(sql);
    res.json({ body });
  },
  FormularioCMP: async (req, res) => {
    const sql = `SELECT * FROM Formulario WHERE comuna = ? AND manzana = ? AND predio = ?`;
    const { comuna, manzana, predio } = req.body;
    const body = await executeQuery2(sql, [comuna, manzana, predio]);
    res.json({ body });
  },
  MultipropietrioTables: async (req, res) => {
    const sql = `SELECT * FROM Multipropietario`;
    const body = await executeQuery2(sql);
    res.json({ body });
  },
  MultipropietrioCMP: async (req, res) => {
    const sql = `SELECT * FROM Multipropietario WHERE comuna = ? AND manzana = ? AND predio = ?`;
    const { comuna, manzana, predio } = req.body;
    const body = await executeQuery2(sql, [comuna, manzana, predio]);
    res.json({ body });
  },
};

module.exports = lookupDBController2;
