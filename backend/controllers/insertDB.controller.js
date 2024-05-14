const query = require("../helper/query")

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
};

module.exports = insertDBController;
