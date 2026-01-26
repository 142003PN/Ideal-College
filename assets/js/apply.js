(() => {
        'use strict';

        document.addEventListener('DOMContentLoaded', () => {

            const form = document.getElementById('admissionForm');
            if (!form) return;

            /* ===============================
            BOOTSTRAP VALIDATION
            =============================== */
            form.addEventListener('submit', e => {
                if (!form.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                form.classList.add('was-validated');
            });

            /* ======LIGHT INPUT SANITIZATION======= */
            form.addEventListener('input', e => {
                const el = e.target;

                switch (el.id) {

                    case 'NRC':
                        el.value = el.value
                            .replace(/[^0-9/]/g, '')
                            .slice(0, 20);
                        break;

                    case 'phone':
                        el.value = el.value
                            .replace(/[^0-9+-]/g, '')
                            .slice(0, 15);
                        break;

                    case 'first_name':
                        el.value = el.value.slice(0, 24);
                        break;

                    case 'last_name':
                        el.value = el.value.slice(0, 15);
                        break;
                }
            });

            /* ===============================
            DISABILITY DEPENDENCY
            =============================== */
            const disability = document.getElementById('Disability');
            const disabilityDesc = document.getElementById('disability_desc');

            if (disability && disabilityDesc) {
                const toggleDisability = () => {
                    const isYes = disability.value === 'Yes';
                    disabilityDesc.disabled = !isYes;
                    disabilityDesc.required = isYes;
                    if (!isYes) disabilityDesc.value = '';
                };

                disability.addEventListener('change', toggleDisability);
                toggleDisability(); // initial state
            }

        });
    })();