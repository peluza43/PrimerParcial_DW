CREATE TABLE IF NOT EXISTS retos (
  id SERIAL PRIMARY KEY,
  titulo VARCHAR(255) NOT NULL,
  descripcion TEXT NOT NULL,
  categoria VARCHAR(100) NOT NULL,
  dificultad VARCHAR(10) NOT NULL CHECK (dificultad IN ('bajo','medio','alto')),
  estado VARCHAR(12) NOT NULL CHECK (estado IN ('pendiente','en proceso','completado')),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ret_cat_dif
ON retos (categoria, dificultad);
