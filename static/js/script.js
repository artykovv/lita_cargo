// Функция для получения товаров и обновления таблицы
async function updateTable() {
    const result = await fetch('/api/v1/routes/get-info'); // замените на нужный эндпоинт
    const data = await result.json();

    var tbody = document.getElementById('tableBody');

    // Очистить таблицу перед обновлением
    tbody.innerHTML = "";

    // Добавление каждого товара в таблицу
    for (var i = 0; i < data.length; i++) {
        var tr = document.createElement('tr');
        
        var checkboxTd = document.createElement('td');
        var checkbox = document.createElement('input');
        checkbox.setAttribute('type', 'checkbox');
        checkbox.setAttribute('data-id', data[i].id);
        checkbox.classList.add('form-check-input');
        checkboxTd.appendChild(checkbox);
        tr.appendChild(checkboxTd);

        var trackCodeTd = document.createElement('td');
        trackCodeTd.innerText = data[i].product_code;
        tr.appendChild(trackCodeTd);

        var idTd = document.createElement('td');
        idTd.innerText = data[i].client_id;
        tr.appendChild(idTd);

        var weightTd = document.createElement('td');
        weightTd.innerText = data[i].weight ? data[i].weight : "N/A";
        tr.appendChild(weightTd);

        var amountTd = document.createElement('td');
        amountTd.innerText = data[i].amount ? data[i].amount : "N/A";
        tr.appendChild(amountTd);

        var statusTd = document.createElement('td');
        statusTd.innerText = translateStatus(data[i].status);
        tr.appendChild(statusTd);

        var dateTd = document.createElement('td');
        dateTd.innerText = new Date(data[i].date).toLocaleDateString();
        tr.appendChild(dateTd);

        tbody.appendChild(tr);
    }
}

// Функция перевода статусов товаров
function translateStatus(status) {
    switch(status) {
        case 'IN_TRANSIT':
            return 'В пути';
        case 'IN_WAREHOUSE':
            return 'Можно забирать';
        case 'PICKED_UP':
            return 'Забрали';
        default:
            return 'Неизвестный статус';
    }
}

// Вызываем функцию updateTable при загрузке страницы
window.onload = updateTable;