use pyo3::prelude::*;
use opencv::{
    core,
    imgcodecs,
    prelude::*,
    videoio,
};
use std::fs;
use std::path::Path;
use std::fs::File;
use std::io::BufReader;

#[pyfunction]
#[pyo3(signature = (video_path, output_dir="data/temp/frames", interval=30))]
fn extract_frames_rust(video_path: &str, output_dir: &str, interval: usize) -> PyResult<Vec<String>> {
    // 1. Crear el directorio si no existe (manejando el error para Python)
    if !Path::new(output_dir).exists() {
        fs::create_dir_all(output_dir)
            .map_err(|e| pyo3::exceptions::PyIOError::new_err(format!("Error creando directorio: {}", e)))?;
    }

    // 2. Abrir el video de forma segura
    let mut cap = videoio::VideoCapture::from_file(video_path, videoio::CAP_ANY)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Error abriendo video: {}", e)))?;

    let mut frame_count = 0;
    let mut saved_frames = Vec::new();
    let mut frame = core::Mat::default();

    // 3. Bucle ultrarrápido de extracción
    loop {
        let ret = cap.read(&mut frame)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Error leyendo frame: {}", e)))?;
        
        if !ret {
            break; // Llegamos al final del video
        }

        if frame_count % interval == 0 {
            // Generar la ruta del archivo
            let frame_name = format!("{}/frame_{}.jpg", output_dir, frame_count);
            
            // Guardar la imagen en disco
            let params = core::Vector::new();
            imgcodecs::imwrite(&frame_name, &frame, &params)
                .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Error guardando imagen: {}", e)))?;
            
            saved_frames.push(frame_name);
        }

        frame_count += 1;
    }

    Ok(saved_frames)
}


/// Definición del módulo de Python implementado en Rust.
/// El nombre de la función aquí DEBE coincidir con el `name` en tu Cargo.toml
#[pymodule]
fn rust_engine(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(extract_frames_rust, m)?)?;
    
    Ok(())
}