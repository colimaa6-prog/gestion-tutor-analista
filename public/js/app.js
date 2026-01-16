document.addEventListener('DOMContentLoaded', () => {


    const loginForm = document.getElementById('loginForm');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const submitBtn = loginForm.querySelector('button[type="submit"]');

            // Visual feedback
            const originalText = submitBtn.innerText;
            submitBtn.innerText = 'Verificando...';
            submitBtn.disabled = true;

            try {
                console.log('Attempting login for:', username);

                const response = await fetch(`${API_BASE_URL}/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });

                // Intentar parsear como JSON directamente
                const text = await response.text();

                try {
                    const data = JSON.parse(text);
                    if (response.ok && data.success) {
                        console.log('Login successful:', data.user);
                        sessionStorage.setItem('user', JSON.stringify(data.user));
                        window.location.href = 'dashboard.html';
                    } else {
                        throw new Error(data.message || 'Error desconocido');
                    }
                } catch (parseError) {
                    console.error("Respuesta no válida del servidor:", text);
                    throw new Error("El servidor respondió con un formato inválido. Revisa la consola.");
                }

            } catch (error) {
                console.error('Login error:', error);
                showToast(error.message || 'Error al intentar iniciar sesión', 'error');
            } finally {
                submitBtn.innerText = originalText;
                submitBtn.disabled = false;
            }
        });
    }
});
