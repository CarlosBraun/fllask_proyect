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

module.exports = executeQuery;