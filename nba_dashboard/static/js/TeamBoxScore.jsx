import React from "react";
import ReactTable from 'react-table'
import { mapMultipleRowsToCol, constructReactTableColumns, HEADER_MAP } from './utils'
import { PlayerLogs } from './PlayerLogs'


const IGNORE_STATS = new Set([
    'GAME_ID',
    'FTA',
    'FTM',
    'FT_PCT',
    'PF',
    'TEAM_ABBREVIATION',
    'COMMENT',
    'FG3A',
    'FGA',
    'PLAYER_ID'
]);

const COLUMN_WIDTHS = {
    'PLAYER_NAME': 120,
    'GAME_DATE': 90,
    'MATCHUP': 90
};

const MAX_PLAYERS_PER_TEAM = 14;

const TEAM_BOX_SCORE_TABLE_STYLE = {
    width: '48%',
    fontSize: '12px',
    float: 'left',
    margin: '10px',
    textAlign: 'center'
};

export class TeamBoxScore extends React.Component {
    render() {
        const columnNames = this.props.statNames;
        const header = this.props.teamName;
        const columns = constructReactTableColumns(columnNames, COLUMN_WIDTHS, HEADER_MAP, IGNORE_STATS);
        const mappedRows = mapMultipleRowsToCol(columnNames, this.props.players);
        return (<ReactTable
            className={'-striped -highlight'}
            data={mappedRows}
            columns={[
                {
                    Header: header,
                    columns: columns
                }
            ]}
            Header={this.props.teamName}
            SubComponent={
                (row) => {
                    return (<PlayerLogs playerId={row.original.PLAYER_ID} />);
                }
            }
            showPagination={false}
            showPageJump={false}
            defaultPageSize={MAX_PLAYERS_PER_TEAM}
            style={TEAM_BOX_SCORE_TABLE_STYLE}
        />);
    }
}
