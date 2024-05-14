const query = require("../helper/query");
const { MultipropietrioCMP } = require("./lookupDB.controller");

const insertDBController = {
  Formulario: async (numeroAtencion, CNE, comuna, manzana, predio, fojas, fechaInscripcion, nroInscripcion) => {
    const sql = `
    INSERT INTO Formulario 
        (numero_atencion, cne, comuna, manzana, predio, fojas, fecha_inscripcion, numero_inscripcion) 
    VALUES 
        (?, ?, ?, ?, ?, ?, ?, ?)
    `;
    return await query(sql, [numeroAtencion, CNE, comuna, manzana, predio, fojas, fechaInscripcion, nroInscripcion]);
  },
  Enajenante: async (RUNRUT, porcDerecho, formularioId) => {
    const sql = `
    INSERT INTO Enajenante 
        (runrut, porc_derecho, formulario_id) 
    VALUES 
        (?, ?, ?)
    `;
    return await query(sql, [RUNRUT, porcDerecho, formularioId]);
  },
  Adquiriente: async (RUNRUT, porcDerecho, formularioId) => {
    const sql = `
    INSERT INTO Adquirente
        (runrut_adq, porc_derecho_adq, formulario_id) 
    VALUES 
        (?, ?, ?)
    `;
    return await query(sql, [RUNRUT, porcDerecho, formularioId]);
  },
  Multipropietrio: async (comuna, manzana, predio, run, derecho, fojas, fecha_inscripcion, ano_inscripccion, numero_inscripcion, ano_vigencia_i, ano_vigencia_f) => {
    const sql = `
    INSERT INTO Multipropietario
        (comuna, manzana, predio, run, derecho, fojas, fecha_inscripcion, ano_inscripccion, numero_inscripcion, ano_vigencia_i, ano_vigencia_f)
    VALUES
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;
    return await query(sql, [comuna, manzana, predio, run, derecho, fojas, fecha_inscripcion, ano_inscripccion, numero_inscripcion, ano_vigencia_i, ano_vigencia_f]);
  },
};

module.exports = insertDBController;
