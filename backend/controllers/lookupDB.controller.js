const pool = require("../database");

const executeQuery = async (sql, parameters) => {
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

const lookupDBController = {
  EnajenanteTables: async (req) => {
    const sql = `SELECT * FROM Enajenante`;
    return await executeQuery(sql);
  },
  AdquirienteTables: async (req) => {
    const sql = `SELECT * FROM Adquirente`;
    return await executeQuery(sql);
  },
  FormularioTables: async (req) => {
    const sql = `SELECT * FROM Formulario`;
    return await executeQuery(sql);
  },
  FormularioCMP: async (req) => {
    const sql = `SELECT * FROM Formulario WHERE comuna = ? AND manzana = ? AND predio = ?`;
    const { comuna, manzana, predio } = req.body;
    return await executeQuery(sql, [comuna, manzana, predio]);
  },
  MultipropietrioTables: async (req) => {
    const sql = `SELECT * FROM Multipropietario`;
    return await executeQuery(sql);
  },
  MultipropietrioCMP: async (req) => {
    const sql = `SELECT * FROM Multipropietario WHERE comuna = ? AND manzana = ? AND predio = ?`;
    const { comuna, manzana, predio } = req.body;
    return await executeQuery(sql, [comuna, manzana, predio]);
  },
};

module.exports = lookupDBController;
