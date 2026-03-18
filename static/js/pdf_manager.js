// Gestión Moderna de PDFs del Chatbot
document.addEventListener('DOMContentLoaded', function () {
    const pdfModal = document.getElementById('pdfModal');

    if (!pdfModal) return;

    const uploadArea = document.getElementById('uploadArea');
    const pdfFileInput = document.getElementById('pdfFileInput');
    const uploadButton = document.getElementById('uploadButton');
    const selectedFileInfo = document.getElementById('selectedFileInfo');
    const uploadProgress = document.getElementById('uploadProgress');
    const uploadResult = document.getElementById('uploadResult');
    const pdfListContent = document.getElementById('pdfListContent'); // Referencia global
    let selectedFile = null;

    // --- DELEGACIÓN DE EVENTOS (Solución Robusta) ---
    // Manejar clicks en botones dentro de la lista, incluso si se regenera el HTML
    if (pdfListContent) {
        pdfListContent.addEventListener('click', function (e) {
            // Botón Activar
            const activeBtn = e.target.closest('.set-active-btn');
            if (activeBtn) {
                const filename = activeBtn.getAttribute('data-filename');
                setActivePdf(filename);
                return;
            }

            // Botón Eliminar
            const deleteBtn = e.target.closest('.delete-pdf-btn');
            if (deleteBtn) {
                const filename = deleteBtn.getAttribute('data-filename');
                deletePdf(filename);
                return;
            }
        });
    }

    // Cargar información de PDFs cuando se abre el modal
    pdfModal.addEventListener('show.bs.modal', function () {
        console.log('Modal opening, loading PDF list...');
        loadPdfList();
    });

    // También intentar cargar al hacer click en el botón que abre el modal (redundancia)
    const openBtn = document.querySelector('[data-bs-target="#pdfModal"]');
    if (openBtn) {
        openBtn.addEventListener('click', function () {
            setTimeout(loadPdfList, 100);
        });
    }

    // Agregar botón de actualización manual
    const pdfListHeader = document.querySelector('#currentPdfInfo h6');
    if (pdfListHeader && !document.getElementById('refreshPdfList')) {
        const refreshBtn = document.createElement('button');
        refreshBtn.id = 'refreshPdfList';
        refreshBtn.className = 'btn btn-sm btn-link float-end p-0';
        refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Actualizar';
        refreshBtn.onclick = function (e) {
            e.preventDefault();
            loadPdfList();
        };
        pdfListHeader.appendChild(refreshBtn);
    }

    function loadPdfList() {
        pdfListContent.innerHTML = '<p class="text-muted"><i class="fas fa-spinner fa-spin me-2"></i>Cargando información...</p>';

        // Agregar timestamp para evitar caché del navegador
        fetch('/moderator/pdf_info?t=' + new Date().getTime())
            .then(response => {
                if (!response.ok) throw new Error('Error en la respuesta del servidor');
                return response.json();
            })
            .then(data => {
                if (data.pdfs && data.pdfs.length > 0) {
                    let html = '<div class="row g-3">';

                    // Encontrar el hash del archivo activo (tesis1234.pdf)
                    const activePdf = data.pdfs.find(p => p.filename === 'tesis1234.pdf');
                    const activeHash = activePdf ? activePdf.hash : null;
                    let activeMarked = false; // Bandera para asegurar solo un activo visual

                    let visiblePdfsCount = 0;

                    data.pdfs.forEach(pdf => {
                        // Ocultar tesis1234.pdf de la lista visual
                        if (pdf.filename === 'tesis1234.pdf') return;

                        visiblePdfsCount++;

                        // Determinar si este archivo es el activo comparando hashes
                        // Solo marcar el primero que encontremos como activo
                        let isActive = false;
                        if (!activeMarked && activeHash && pdf.hash === activeHash) {
                            isActive = true;
                            activeMarked = true;
                        }

                        const cardClass = isActive ? 'border-success shadow' : 'border-light';
                        const badgeClass = isActive ? 'bg-success' : 'bg-secondary';
                        const badgeText = isActive ? 'ACTIVO' : 'En Biblioteca';
                        const iconClass = isActive ? 'text-success' : 'text-danger';

                        html += `
                            <div class="col-md-6">
                                <div class="card ${cardClass} pdf-card h-100" data-filename="${pdf.filename}">
                                    <div class="card-body">
                                        <div class="d-flex justify-content-between align-items-start mb-2">
                                            <h6 class="card-title mb-0 text-truncate" title="${pdf.filename}">
                                                <i class="fas fa-file-pdf ${iconClass} me-2"></i>
                                                ${pdf.filename}
                                            </h6>
                                            <span class="badge ${badgeClass}">${badgeText}</span>
                                        </div>
                                        <p class="card-text small text-muted mb-3">
                                            <i class="fas fa-hdd me-1"></i> ${pdf.size}<br>
                                            <i class="fas fa-clock me-1"></i> ${pdf.modified}
                                        </p>
                                        <div class="btn-group w-100" role="group">
                                            ${!isActive ? `
                                                <button class="btn btn-sm btn-outline-primary set-active-btn" data-filename="${pdf.filename}">
                                                    <i class="fas fa-play-circle"></i> Activar este PDF
                                                </button>
                                            ` : `
                                                <button class="btn btn-sm btn-success" disabled>
                                                    <i class="fas fa-check-circle"></i> Activo
                                                </button>
                                            `}
                                            <button class="btn btn-sm btn-danger delete-pdf-btn" data-filename="${pdf.filename}"
                                                    ${isActive ? 'disabled title="No puedes eliminar el PDF activo"' : ''}>
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;
                    });

                    html += '</div>';

                    if (visiblePdfsCount === 0) {
                        pdfListContent.innerHTML = `
                            <div class="alert alert-warning">
                                <i class="fas fa-exclamation-triangle me-2"></i>
                                No hay PDFs visibles en la biblioteca. Sube uno nuevo.
                            </div>
                        `;
                    } else {
                        pdfListContent.innerHTML = html;
                        // Ya no necesitamos llamar a addEventListeners() aquí gracias a la delegación
                    }

                } else {
                    pdfListContent.innerHTML = `
                        <div class="alert alert-warning">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            No hay PDFs en la carpeta tesis. Sube uno para comenzar.
                        </div>
                    `;
                }
            })
            .catch(error => {
                console.error('Error loading PDFs:', error);
                pdfListContent.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-times me-2"></i>Error al cargar información: ${error.message}
                    </div>
                `;
            });
    }

    function setActivePdf(filename) {
        if (!confirm(`¿Deseas usar "${filename}" como PDF activo del chatbot?`)) {
            return;
        }

        // Usar encodeURIComponent para manejar nombres con espacios o caracteres especiales
        fetch(`/moderator/set_active_pdf/${encodeURIComponent(filename)}`, {
            method: 'POST'
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showResult('success', data.message);
                    loadPdfList(); // Recargar la lista
                } else {
                    showResult('danger', data.error);
                }
            })
            .catch(error => {
                showResult('danger', 'Error de conexión: ' + error.message);
            });
    }

    function deletePdf(filename) {
        if (!confirm(`¿Estás seguro de que deseas eliminar "${filename}"?`)) {
            return;
        }

        // Usar encodeURIComponent
        fetch(`/moderator/delete_pdf/${encodeURIComponent(filename)}`, {
            method: 'DELETE'
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showResult('success', data.message);
                    loadPdfList();
                } else {
                    showResult('danger', data.error);
                }
            })
            .catch(error => {
                showResult('danger', 'Error de conexión: ' + error.message);
            });
    }

    // Drag and drop
    if (uploadArea) {
        uploadArea.addEventListener('dragover', function (e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', function (e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', function (e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelect(files[0]);
            }
        });

        uploadArea.addEventListener('click', function () {
            pdfFileInput.click();
        });
    }

    if (pdfFileInput) {
        pdfFileInput.addEventListener('change', function (e) {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });
    }

    function handleFileSelect(file) {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            showResult('danger', 'Por favor selecciona un archivo PDF válido');
            return;
        }

        selectedFile = file;
        document.getElementById('selectedFileName').textContent = file.name;
        document.getElementById('selectedFileSize').textContent = formatFileSize(file.size);
        selectedFileInfo.style.display = 'block';
        uploadButton.disabled = false;
        uploadResult.style.display = 'none';
    }

    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' bytes';
        else if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
        else return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    }

    if (uploadButton) {
        uploadButton.addEventListener('click', function () {
            if (!selectedFile) {
                showResult('warning', 'Por favor selecciona un archivo PDF');
                return;
            }

            const formData = new FormData();
            formData.append('pdf_file', selectedFile);

            uploadProgress.style.display = 'block';
            uploadButton.disabled = true;
            uploadResult.style.display = 'none';

            const progressBar = uploadProgress.querySelector('.progress-bar');
            progressBar.style.width = '30%';

            fetch('/moderator/upload_pdf', {
                method: 'POST',
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    progressBar.style.width = '100%';
                    setTimeout(() => {
                        uploadProgress.style.display = 'none';
                        if (data.success) {
                            showResult('success', data.message || 'PDF subido correctamente.');
                            loadPdfList();
                            selectedFileInfo.style.display = 'none';
                            selectedFile = null;
                            pdfFileInput.value = '';
                        } else {
                            showResult('danger', data.error || 'Error al subir el PDF');
                            uploadButton.disabled = false;
                        }
                    }, 500);
                })
                .catch(error => {
                    uploadProgress.style.display = 'none';
                    showResult('danger', 'Error de conexión: ' + error.message);
                    uploadButton.disabled = false;
                });
        });
    }

    function showResult(type, message) {
        uploadResult.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'times-circle' : 'exclamation-triangle'} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        uploadResult.style.display = 'block';
    }
});
