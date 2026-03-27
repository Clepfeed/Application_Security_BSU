document.addEventListener('DOMContentLoaded', () => {
    const playersList = document.getElementById('playersList');
    const addPlayerBtn = document.getElementById('addPlayerBtn');
    const matchForm = document.getElementById('matchForm');

    const settingsBtn = document.getElementById('settingsBtn');
    const settingsDropdown = document.getElementById('settingsDropdown');
    const sslToggle = document.getElementById('sslToggle');
    const sslStatus = document.getElementById('sslStatus');

    settingsBtn.addEventListener('click', (event) => {
        event.stopPropagation();
        settingsDropdown.classList.toggle('show');
    });

    document.addEventListener('click', (event) => {
        if (!settingsDropdown.contains(event.target) && event.target !== settingsBtn) {
            settingsDropdown.classList.remove('show');
        }
    });

    // Смена сертификата
    sslToggle.addEventListener('change', async (event) => {
        const isValid = event.target.checked;
        
        sslStatus.textContent = isValid ? 'Валидный' : 'Невалидный';
        sslStatus.className = isValid ? 'status-valid' : 'status-invalid';

        console.log(`[DEV] Change TLS request to ${isValid ? 'ВАЛИДНЫЙ' : 'НЕВАЛИДНЫЙ'}...`);
 
        try {
            const response = await fetch('/api/dev/switch-cert', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ useValidCert: isValid })
            });

            if (!response.ok) throw new Error('Server Error change TLS');
            console.log('[DEV] TLS Changed');
        } catch (error) {
            console.error('[DEV] Error:', error);
            alert('Server Error TLS change');

            sslToggle.checked = !isValid; 
            sslStatus.textContent = !isValid ? 'Валидный' : 'Невалидный';
            sslStatus.className = !isValid ? 'status-valid' : 'status-invalid';
        }
    });

    // Функция для обновления нумерации игроков
    function updatePlayerNumbers() {
        const rows = playersList.querySelectorAll('.player-row');
        rows.forEach((row, index) => {
            row.querySelector('.player-number').textContent = `${index + 1}.`;
        });
    }

    // Добавление новой строки для игрока
    addPlayerBtn.addEventListener('click', () => {
        const newRow = document.createElement('div');
        newRow.className = 'player-row';
        
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'player-input';
        input.placeholder = 'Имя и Фамилия игрока';
        input.required = true;

        const numberSpan = document.createElement('span');
        numberSpan.className = 'player-number';

        newRow.appendChild(numberSpan);
        newRow.appendChild(input);
        playersList.appendChild(newRow);

        updatePlayerNumbers();
    });

    // Обработка отправки формы
    matchForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Предотвращаем перезагрузку страницы

        const date = document.getElementById('matchDate').value;
        const team = document.getElementById('teamName').value;
        const playerInputs = document.querySelectorAll('.player-input');
        const players = Array.from(playerInputs).map(input => input.value.trim());

        const matchData = {
            date: date,
            team: team,
            players: players
        };

        try {
            const response = await fetch('/api/match', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(matchData)
            });

            if (response.ok) {
                console.log("Data sended")
            } else {
                alert("Error with data save");
            }
        } catch (error) {
            console.error("Sever error", error);
            alert('Не удалось подключиться к с');
        }

        matchForm.reset();
        playersList.innerHTML = `
            <div class="player-row">
                <span class="player-number">1.</span>
                <input type="text" class="player-input" placeholder="Имя и Фамилия игрока" required>
            </div>
        `;
    });
});