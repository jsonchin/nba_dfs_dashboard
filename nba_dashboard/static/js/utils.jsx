import React from "react";

const SHARED_COLUMN_WIDTHS = {
    'PLAYER_NAME': 120,
    'GAME_DATE': 80,
    'MATCHUP': 90,
    'DK_FP': 60
};

export const HEADER_MAP = {
    'TEAM_ABBREVIATION': 'Team',
    'PLAYER_NAME': 'Player',
    'START_POSITION': 'P',
    'PLUS_MINUS': '+/-',
    'FG_PCT': 'FG%',
    'FG3_PCT': 'FG3%',
    'FT_PCT': 'FT%',
    'NBA_TO': 'TOV',
    'GAME_DATE': 'Game Date',
    'MATCHUP': 'Matchup'
};

export function mapMultipleRowsToCol(colNames, rows) {
    return rows.map((row) => mapRowToCol(colNames, row));
};

/**
 * Creates the columns prop for ReactTable.
 * @param {String[]} colNames 
 * @param {Object} columnWidths 
 * @param {Object} headerMapping
 */
export function constructReactTableColumns(colNames, columnWidths, headerMapping) {
    const reactTableColumns = [];
    colNames.forEach((colName) => {
        let width = undefined; // undefined is okay
        if (colName in columnWidths) { // look at passed in mapping first
            width = columnWidths[colName];
        } else if (colName in SHARED_COLUMN_WIDTHS) { // then look at shared if not found in passed in
            width = SHARED_COLUMN_WIDTHS[colName];
        }

        let header = colName;
        if (headerMapping && colName in headerMapping) {
            header = headerMapping[colName];
        } else if (colName in HEADER_MAP) {
            header = HEADER_MAP[colName];
        }

        const colProps = {
            'Header': <b>{header}</b>,
            'accessor': colName,
            'width': width,
            'minWidth': undefined
        };
        reactTableColumns.push(colProps);
    });
    return reactTableColumns;
};

const mapRowToCol = function mapRowToColDictionary(colNames, rowValues) {
    const mapping = {};
    for (let i = 0; i < colNames.length; i += 1) {
        mapping[colNames[i]] = rowValues[i];
    }
    return mapping;
};
