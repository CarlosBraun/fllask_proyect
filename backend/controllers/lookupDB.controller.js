const query = require("../helper/query.js")

const lookupDBController = {
  EnajenanteTables: async () => {
    const sql = `SELECT * FROM Enajenante`;
    return await query(sql);
  },
  EnajenanteID: async (id) => {
    const sql = `SELECT * FROM Enajenante WHERE formulario_id = ?`;
    return await query(sql, [id]);
  },
  AdquirienteTables: async () => {
    const sql = `SELECT * FROM Adquirente`;
    return await query(sql);
  },
  AdquirienteID: async (id) => {
    const sql = `SELECT * FROM Adquirente WHERE formulario_id = ?`;
    return await query(sql, [id]);
  },
  FormularioTables: async () => {
    const sql = `SELECT * FROM Formulario`;
    return await query(sql);
  },
  FormularioCMP: async (comuna, manzana, predio) => {
    const sql = `SELECT * FROM Formulario WHERE comuna = ? AND manzana = ? AND predio = ?`;
    return await query(sql, [comuna, manzana, predio]);
  },
  FormularioYear: async (year) => {
    const sql = `SELECT * FROM Formulario WHERE YEAR(fecha_inscripcion) = ?`;
    return await query(sql, [year]);
  },
  FormularioAtencion: async (numero_atencion) => {
    const sql = `SELECT * FROM Formulario WHERE numero_atencion = ?`
    return await query(sql, [numero_atencion]);
  },
  FormularioUltimoNumneroAtencion: async () => {
    const sql = `SELECT numero_atencion FROM Formulario ORDER BY id DESC LIMIT 1`;
    return await query(sql);
  },
  MultipropietrioTables: async () => {
    const sql = `SELECT * FROM Multipropietario`;
    return await query(sql);
  },
  MultipropietrioCMP: async (comuna, manzana, predio) => {
    const sql = `SELECT * FROM Multipropietario WHERE comuna = ? AND manzana = ? AND predio = ?`;
    return await query(sql, [comuna, manzana, predio]);
  },
  MultipropietrioYear: async (year) => {
    const sql = `SELECT * FROM Multipropietario WHERE YEAR(fecha_inscripcion) = ?`;
    return await query(sql, [year]);
  },
};

module.exports = lookupDBController;
