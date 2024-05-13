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
  EnajenanteTables: async () => {
    const sql = `SELECT * FROM Enajenante`;
    return await executeQuery(sql);
  },
  EnajenanteID: async (id) => {
    const sql = `SELECT * FROM Enajenante WHERE formulario_id = ?`;
    return await executeQuery(sql, [id]);
  },
  AdquirienteTables: async () => {
    const sql = `SELECT * FROM Adquirente`;
    return await executeQuery(sql);
  },
  AdquirienteID: async (id) => {
    const sql = `SELECT * FROM Adquirente WHERE formulario_id = ?`;
    return await executeQuery(sql, [id]);
  },
  FormularioTables: async () => {
    const sql = `SELECT * FROM Formulario`;
    return await executeQuery(sql);
  },
  FormularioCMP: async (comuna, manzana, predio) => {
    const sql = `SELECT * FROM Formulario WHERE comuna = ? AND manzana = ? AND predio = ?`;
    return await executeQuery(sql, [comuna, manzana, predio]);
  },
  FormularioYear: async (year) => {
    const sql = `SELECT * FROM Formulario WHERE YEAR(fecha_inscripcion) = ?`;
    return await executeQuery(sql, [year]);
  },
  FormularioAtencion: async (numero_atencion) => {
    const sql = `SELECT * FROM Formulario WHERE numero_atencion = ?`
    return await executeQuery(sql, [numero_atencion]);
  },
  MultipropietrioTables: async () => {
    const sql = `SELECT * FROM Multipropietario`;
    return await executeQuery(sql);
  },
  MultipropietrioCMP: async (comuna, manzana, predio) => {
    const sql = `SELECT * FROM Multipropietario WHERE comuna = ? AND manzana = ? AND predio = ?`;
    return await executeQuery(sql, [comuna, manzana, predio]);
  },
  MultipropietrioYear: async (year) => {
    const sql = `SELECT * FROM Multipropietario WHERE YEAR(fecha_inscripcion) = ?`;
    return await executeQuery(sql, [year]);
  },
};

module.exports = lookupDBController;
