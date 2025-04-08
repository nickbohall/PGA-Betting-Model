// API base URL - update this to match your FastAPI server
const API_BASE_URL = 'http://localhost:8000';

// DOM elements
const tabButtons = document.querySelectorAll('.tab-button');
const tabContents = document.querySelectorAll('.tab-content');
const notification = document.getElementById('notification');

// Action buttons
const refreshPlayersBtn = document.getElementById('refreshPlayers');
const refreshTournamentsBtn = document.getElementById('refreshTournaments');
const refreshPlayerStatsBtn = document.getElementById('refreshPlayerStats');
const addTournamentBtn = document.getElementById('addTournament');
const updateResultsBtn = document.getElementById('updateResults');
const addPlayerStatsBtn = document.getElementById('addPlayerStats');
const refreshMasterBtn = document.getElementById('refreshMaster');
const applyMasterFilterBtn = document.getElementById('applyMasterFilter');
const resetMasterFilterBtn = document.getElementById('resetMasterFilter');

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    // Set up tab switching
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            button.classList.add('active');
            const tabId = `${button.dataset.tab}-tab`;
            document.getElementById(tabId).classList.add('active');
            
            // Load data for the active tab
            loadTabData(button.dataset.tab);
        });
    });
    
    // Set up action button event listeners
    refreshPlayersBtn.addEventListener('click', refreshPlayers);
    refreshTournamentsBtn.addEventListener('click', refreshTournaments);
    refreshPlayerStatsBtn.addEventListener('click', refreshPlayerStats);
    addTournamentBtn.addEventListener('click', addTournament);
    updateResultsBtn.addEventListener('click', updateTournamentResults);
    addPlayerStatsBtn.addEventListener('click', addPlayerStatsForTournament);
    refreshMasterBtn.addEventListener('click', refreshMasterData);
    applyMasterFilterBtn.addEventListener('click', () => {
        const tournament = document.getElementById('masterFilterTournament').value;
        const year = document.getElementById('masterFilterYear').value;
        loadMasterData(tournament, year);
    });
    resetMasterFilterBtn.addEventListener('click', () => {
        document.getElementById('masterFilterTournament').value = '';
        document.getElementById('masterFilterYear').value = '';
        loadMasterData();
    });
    
    // Load initial data for the active tab
    const activeTab = document.querySelector('.tab-button.active').dataset.tab;
    loadTabData(activeTab);
});

// Load data for the specified tab
function loadTabData(tab) {
    switch(tab) {
        case 'players':
            loadPlayersData();
            break;
        case 'playerStats':
            loadPlayerStatsData();
            break;
        case 'tournaments':
            loadTournamentsData();
            break;
        case 'master':
            loadMasterData();
            break;
    }
}

// API request helper function
async function apiRequest(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (data && (method === 'POST' || method === 'PATCH' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'API request failed');
        }
        
        return await response.json();
    } catch (error) {
        let errorMessage = error.message;
        
        // Try to extract more detailed error information if available
        if (error instanceof Response || (error.response && error.response instanceof Response)) {
            try {
                const errorData = await error.json();
                if (errorData && errorData.detail) {
                    errorMessage = errorData.detail;
                }
            } catch (e) {
                // If we can't parse the error response, just use the original message
                console.error('Error parsing error response:', e);
            }
        }
        
        showNotification(errorMessage, true);
        console.error('API Error:', error);
        return null;
    }
}

// Load players data
async function loadPlayersData() {
    try {
        const players = await apiRequest('/players/');
        if (players) {
            renderTable('players-table', players, ['id', 'name', 'nationality']);
        }
    } catch (error) {
        // If there's an error, display a message in the table container
        const container = document.getElementById('players-table');
        container.innerHTML = `<p class="error-message">Error loading players data. The PGA Tour website may be blocking automated access. Please try again later.</p>`;
    }
}

// Load player stats data
async function loadPlayerStatsData() {
    const playerStats = await apiRequest('/player-stats/');
    if (playerStats) {
        renderTable('playerStats-table', playerStats, ['name', 'id', 'sg_total', 'sg_ttg', 'sg_ott', 'sg_apr', 'sg_atg', 'sg_putt']);
    }
}

// Load tournaments data
async function loadTournamentsData() {
    const tournaments = await apiRequest('/tournaments/');
    if (tournaments) {
        renderTable('tournaments-table', tournaments, ['tournament_name', 'tournament_id', 'course_name', 'year', 'tournament_date']);
    }
}

// Load master data with optional filters
async function loadMasterData(tournament = '', year = '') {
    let endpoint = '/master/';
    const params = [];
    
    if (tournament) {
        params.push(`tournament_name=${encodeURIComponent(tournament)}`);
    }
    
    if (year) {
        params.push(`year=${year}`);
    }
    
    if (params.length > 0) {
        endpoint += `?${params.join('&')}`;
    }
    
    const masterData = await apiRequest(endpoint);
    if (masterData) {
        renderTable('master-table', masterData, [
            'year', 'tournament_id', 'tournament_name', 'course_name', 'player_name',
            'finish', 'score', 'sg_total', 'sg_ttg', 'sg_ott', 'sg_apr', 'sg_atg', 'sg_putt', 'odds'
        ]);
    }
}

// Render data table with sorting and filtering
function renderTable(containerId, data, columns) {
    const container = document.getElementById(containerId);
    
    if (!data || data.length === 0) {
        container.innerHTML = '<p class="no-data">No data available</p>';
        return;
    }
    
    // Store the original data for filtering/sorting
    container.dataset.originalData = JSON.stringify(data);
    
    // Add filter controls and delete table button
    let filterHtml = `
        <div class="filter-controls">
            <select id="${containerId}-filter-column">
                ${columns.map(column => `<option value="${column}">${formatColumnName(column)}</option>`).join('')}
            </select>
            <input type="text" id="${containerId}-filter-value" placeholder="Filter value...">
            <button id="${containerId}-apply-filter">Apply Filter</button>
            <button id="${containerId}-reset-filter">Reset Filters</button>
            <button id="${containerId}-filter-a">Filter Last Names 'A'</button>
            <button id="${containerId}-delete-table" class="delete-table-btn">Delete Entire Table</button>
        </div>
        <div id="${containerId}-active-filters"></div>
    `;
    
    // Add a delete button column for master table
    const showDeleteButton = containerId === 'master-table' || containerId === 'tournaments-table';
    
    let tableHtml = '<table><thead><tr>';
    
    // Create table headers with sorting
    columns.forEach(column => {
        tableHtml += `<th class="sortable" data-column="${column}">${formatColumnName(column)}</th>`;
    });
    
    // Add delete column header if needed
    if (showDeleteButton) {
        tableHtml += `<th>Actions</th>`;
    }
    
    tableHtml += '</tr></thead><tbody>';
    
    // Create table rows
    data.forEach(item => {
        tableHtml += '<tr>';
        columns.forEach(column => {
            tableHtml += `<td>${item[column] !== null ? item[column] : '-'}</td>`;
        });
        
        // Add delete button if needed
        if (showDeleteButton) {
            if (containerId === 'master-table') {
                tableHtml += `<td><button class="delete-btn" data-tournament="${item.tournament_name}" data-year="${item.year}">Delete</button></td>`;
            } else if (containerId === 'tournaments-table') {
                tableHtml += `<td><button class="delete-btn" data-tournament="${item.tournament_name}" data-year="${item.year}">Delete</button></td>`;
            }
        }
        
        tableHtml += '</tr>';
    });
    
    tableHtml += '</tbody></table>';
    container.innerHTML = filterHtml + tableHtml;
    
    // Add event listeners for sorting
    const headers = container.querySelectorAll('th.sortable');
    headers.forEach(header => {
        header.addEventListener('click', () => {
            const column = header.dataset.column;
            const isAsc = header.classList.contains('asc');
            
            // Remove sorting classes from all headers
            headers.forEach(h => {
                h.classList.remove('asc', 'desc');
            });
            
            // Set the new sorting direction
            if (isAsc) {
                header.classList.add('desc');
                sortTable(containerId, column, false);
            } else {
                header.classList.add('asc');
                sortTable(containerId, column, true);
            }
        });
    });
    // Add event listeners for delete buttons
    const deleteButtons = container.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', handleDeleteTable);
    });
    
    // Add event listener for delete table button
    const deleteTableBtn = document.getElementById(`${containerId}-delete-table`);
    if (deleteTableBtn) {
        deleteTableBtn.addEventListener('click', () => handleDeleteEntireTable(containerId));
    }
    
    // Add event listeners for filtering
    const applyFilterBtn = document.getElementById(`${containerId}-apply-filter`);
    const resetFilterBtn = document.getElementById(`${containerId}-reset-filter`);
    const filterABtn = document.getElementById(`${containerId}-filter-a`);
    
    applyFilterBtn.addEventListener('click', () => {
        const column = document.getElementById(`${containerId}-filter-column`).value;
        const value = document.getElementById(`${containerId}-filter-value`).value;
        if (value) {
            applyFilter(containerId, column, value);
        }
    });
    
    resetFilterBtn.addEventListener('click', () => {
        resetFilters(containerId, columns);
    });
    
    filterABtn.addEventListener('click', () => {
        // Special filter for last names starting with 'A'
        if (containerId === 'players-table' || containerId === 'playerStats-table') {
            const nameColumn = containerId === 'players-table' ? 'name' : 'name';
            applyFilter(containerId, nameColumn, '^A', true);
        } else if (containerId === 'master-table') {
            applyFilter(containerId, 'player_name', '^A', true);
        }
    });
}

// Sort table data
function sortTable(containerId, column, ascending) {
    const container = document.getElementById(containerId);
    const tbody = container.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    // Get the index of the column
    const headerCells = container.querySelectorAll('th');
    const columnIndex = Array.from(headerCells).findIndex(cell => cell.dataset.column === column);
    
    // Sort the rows
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent;
        const bValue = b.cells[columnIndex].textContent;
        
        // Handle numeric values
        if (!isNaN(aValue) && !isNaN(bValue)) {
            return ascending ?
                parseFloat(aValue) - parseFloat(bValue) :
                parseFloat(bValue) - parseFloat(aValue);
        }
        
        // Handle text values
        return ascending ?
            aValue.localeCompare(bValue) :
            bValue.localeCompare(aValue);
    });
    
    // Reorder the rows in the DOM
    rows.forEach(row => tbody.appendChild(row));
}

// Apply filter to table
function applyFilter(containerId, column, value, isRegex = false) {
    const container = document.getElementById(containerId);
    const originalData = JSON.parse(container.dataset.originalData);
    const activeFiltersContainer = document.getElementById(`${containerId}-active-filters`);
    
    // Add filter badge if it doesn't exist
    const filterId = `${containerId}-filter-${column}-${value}`;
    if (!document.getElementById(filterId)) {
        const filterBadge = document.createElement('span');
        filterBadge.id = filterId;
        filterBadge.className = 'filter-badge';
        filterBadge.innerHTML = `${formatColumnName(column)}: ${value} <button data-column="${column}" data-value="${value}">×</button>`;
        activeFiltersContainer.appendChild(filterBadge);
        
        // Add event listener to remove filter
        filterBadge.querySelector('button').addEventListener('click', (e) => {
            const column = e.target.dataset.column;
            const value = e.target.dataset.value;
            filterBadge.remove();
            
            // Reapply remaining filters
            reapplyFilters(containerId);
        });
    }
    
    // Filter the data
    let filteredData;
    if (isRegex) {
        const regex = new RegExp(value);
        filteredData = originalData.filter(item => {
            const fieldValue = String(item[column] || '');
            return regex.test(fieldValue);
        });
    } else {
        filteredData = originalData.filter(item => {
            const fieldValue = String(item[column] || '').toLowerCase();
            return fieldValue.includes(value.toLowerCase());
        });
    }
    
    // Re-render the table with filtered data
    const columns = Object.keys(originalData[0] || {});
    renderTableBody(containerId, filteredData, columns);
}

// Reapply all active filters
function reapplyFilters(containerId) {
    const container = document.getElementById(containerId);
    const originalData = JSON.parse(container.dataset.originalData);
    const activeFiltersContainer = document.getElementById(`${containerId}-active-filters`);
    const activeFilters = activeFiltersContainer.querySelectorAll('.filter-badge');
    
    if (activeFilters.length === 0) {
        // No active filters, restore original data
        const columns = Object.keys(originalData[0] || {});
        renderTableBody(containerId, originalData, columns);
        return;
    }
    
    // Apply all active filters
    let filteredData = [...originalData];
    activeFilters.forEach(filter => {
        const button = filter.querySelector('button');
        const column = button.dataset.column;
        const value = button.dataset.value;
        
        filteredData = filteredData.filter(item => {
            const fieldValue = String(item[column] || '').toLowerCase();
            return fieldValue.includes(value.toLowerCase());
        });
    });
    
    // Re-render the table with filtered data
    const columns = Object.keys(originalData[0] || {});
    renderTableBody(containerId, filteredData, columns);
}

// Reset all filters
function resetFilters(containerId, columns) {
    const container = document.getElementById(containerId);
    const originalData = JSON.parse(container.dataset.originalData);
    const activeFiltersContainer = document.getElementById(`${containerId}-active-filters`);
    
    // Clear all filter badges
    activeFiltersContainer.innerHTML = '';
    
    // Reset filter input
    document.getElementById(`${containerId}-filter-value`).value = '';
    
    // Restore original data
    renderTableBody(containerId, originalData, columns);
}

// Render only the table body (for filtering/sorting)
function renderTableBody(containerId, data, columns) {
    const container = document.getElementById(containerId);
    const tbody = container.querySelector('tbody');
    
    if (!tbody || !data || data.length === 0) {
        return;
    }
    
    // Check if we need to show delete buttons
    const showDeleteButton = containerId === 'master-table' || containerId === 'tournaments-table';
    
    let tbodyHtml = '';
    
    // Create table rows
    data.forEach(item => {
        tbodyHtml += '<tr>';
        columns.forEach(column => {
            tbodyHtml += `<td>${item[column] !== null ? item[column] : '-'}</td>`;
        });
        
        // Add delete button if needed
        if (showDeleteButton) {
            if (containerId === 'master-table') {
                tbodyHtml += `<td><button class="delete-btn" data-tournament="${item.tournament_name}" data-year="${item.year}">Delete</button></td>`;
            } else if (containerId === 'tournaments-table') {
                tbodyHtml += `<td><button class="delete-btn" data-tournament="${item.tournament_name}" data-year="${item.year}">Delete</button></td>`;
            }
        }
        
        tbodyHtml += '</tr>';
    });
    
    tbody.innerHTML = tbodyHtml;
    
    // Add event listeners to delete buttons
    if (showDeleteButton) {
        const deleteButtons = tbody.querySelectorAll('.delete-btn');
        deleteButtons.forEach(button => {
            button.addEventListener('click', handleDeleteTable);
        });
    }
    
    // Make sure delete table button has event listener
    const deleteTableBtn = document.getElementById(`${containerId}-delete-table`);
    if (deleteTableBtn) {
        deleteTableBtn.addEventListener('click', () => handleDeleteEntireTable(containerId));
    }
}

// Format column name for display
function formatColumnName(column) {
    return column
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
}

// Refresh players
async function refreshPlayers() {
    const result = await apiRequest('/players/refresh', 'POST');
    if (result) {
        showNotification('Player refresh started');
    }
}

// Refresh tournaments
async function refreshTournaments() {
    const result = await apiRequest('/tournaments/refresh', 'POST');
    if (result) {
        showNotification('Tournament refresh started');
    }
}

// Refresh player stats
async function refreshPlayerStats() {
    const result = await apiRequest('/player-stats/refresh', 'POST');
    if (result) {
        showNotification('Player stats refresh started');
        // Reload the player stats data to show the updated information
        if (document.querySelector('.tab-button.active').dataset.tab === 'playerStats') {
            loadPlayerStatsData();
        }
    }
}

// Add tournament
async function addTournament() {
    const tournamentName = document.getElementById('tournamentName').value;
    const tournamentYear = document.getElementById('tournamentYear').value;
    
    if (!tournamentName || !tournamentYear) {
        showNotification('Please enter tournament name and year', true);
        return;
    }
    
    const result = await apiRequest(`/master/tournaments/${tournamentName}?year=${tournamentYear}`, 'POST');
    if (result) {
        showNotification('Tournament added successfully');
        document.getElementById('tournamentName').value = '';
        document.getElementById('tournamentYear').value = '';
        loadMasterData();
    }
}

// Update tournament results
async function updateTournamentResults() {
    const tournamentName = document.getElementById('resultsTournamentName').value;
    const tournamentYear = document.getElementById('resultsTournamentYear').value;
    
    if (!tournamentName || !tournamentYear) {
        showNotification('Please enter tournament name and year', true);
        return;
    }
    
    const result = await apiRequest(`/master/${tournamentName}/${tournamentYear}/finishes`, 'PATCH');
    if (result) {
        showNotification('Tournament results updated successfully');
        document.getElementById('resultsTournamentName').value = '';
        document.getElementById('resultsTournamentYear').value = '';
        loadMasterData();
    }
}

// Add player stats for tournament
async function addPlayerStatsForTournament() {
    const tournamentName = document.getElementById('playerStatsTournamentName').value;
    const tournamentYear = document.getElementById('playerStatsTournamentYear').value;
    
    if (!tournamentName || !tournamentYear) {
        showNotification('Please enter tournament name and year', true);
        return;
    }
    
    const result = await apiRequest(`/master/${tournamentName}/${tournamentYear}/player-stats`, 'POST');
    if (result) {
        showNotification('Player stats added successfully');
        document.getElementById('playerStatsTournamentName').value = '';
        document.getElementById('playerStatsTournamentYear').value = '';
        loadMasterData();
    }
}

// Refresh master data
async function refreshMasterData() {
    const result = await apiRequest('/master/refresh', 'POST');
    if (result) {
        showNotification('Master data refresh started. This may take a while...');
        // Reload the master data to show the updated information
        if (document.querySelector('.tab-button.active').dataset.tab === 'master') {
            loadMasterData();
        }
    }
}

// Handle delete table button click
async function handleDeleteTable(event) {
    const button = event.target;
    const tournament = button.dataset.tournament;
    const year = button.dataset.year;
    
    if (!tournament || !year) {
        showNotification('Missing tournament or year information', true);
        return;
    }
    
    // Confirm deletion
    if (!confirm(`Are you sure you want to delete ${tournament} (${year})? This action cannot be undone.`)) {
        return;
    }
    
    try {
        const result = await apiRequest(`/master/${tournament}/${year}`, 'DELETE');
        if (result) {
            showNotification(`Successfully deleted ${tournament} (${year})`);
            
            // Reload the current tab data
            const activeTab = document.querySelector('.tab-button.active').dataset.tab;
            loadTabData(activeTab);
        }
    } catch (error) {
        showNotification(`Failed to delete table: ${error.message}`, true);
    }
}

// Handle delete entire table button click
async function handleDeleteEntireTable(containerId) {
    // Map container ID to table name for API endpoint
    const tableMap = {
        'players-table': 'players',
        'playerStats-table': 'player-stats',
        'tournaments-table': 'tournaments',
        'master-table': 'master'
    };
    
    const tableName = tableMap[containerId];
    if (!tableName) {
        showNotification('Unknown table type', true);
        return;
    }
    
    // Confirm deletion
    if (!confirm(`Are you sure you want to delete the ENTIRE ${tableName.replace('-', ' ')} table? This action cannot be undone and will remove ALL data from this table.`)) {
        return;
    }
    
    try {
        const result = await apiRequest(`/${tableName}/delete-all`, 'DELETE');
        if (result) {
            showNotification(`Successfully deleted all data from ${tableName.replace('-', ' ')} table`);
            
            // Reload the current tab data
            const activeTab = document.querySelector('.tab-button.active').dataset.tab;
            loadTabData(activeTab);
        }
    } catch (error) {
        showNotification(`Failed to delete table: ${error.message}`, true);
    }
}

// Show notification
function showNotification(message, isError = false) {
    notification.textContent = message;
    notification.className = 'notification';
    
    if (isError) {
        notification.classList.add('error');
    }
    
    notification.style.display = 'block';
    
    // For errors, keep the notification visible longer
    const timeout = isError ? 5000 : 3000;
    
    setTimeout(() => {
        notification.style.display = 'none';
    }, timeout);
}