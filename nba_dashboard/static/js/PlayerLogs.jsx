import React from "react";
import ReactTable from 'react-table'
import { mapMultipleRowsToCol, constructReactTableColumns } from './utils'
import { TeamBoxScore } from './TeamBoxScore'


const IGNORE_STATS = new Set([
    'GAME_ID',
    'FTA',
    'FTM',
    'FT_PCT',
    'PF',
    'TEAM_ABBREVIATION',
    'FG3A',
    'FGA'
]);

const COLUMN_WIDTHS = {
    'MIN': 40
};

const PLAYER_LOGS_STYLE = {
    width: '100%',
    fontSize: '12px',
    textAlign: 'center',
    marginBottom: '40px'
};

const MAX_LOGS_PER_PAGE = 10;

export class PlayerLogs extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            error: null,
            isLoaded: false,
            data: null
        };

        fetch('/player/' + this.props.playerId + '/logs')
            .then((res) => res.json())
            .then((result) => {
                this.setState({
                    isLoaded: true,
                    data: result
                });
            },
            (error) => {
                this.setState({
                    isLoaded: true,
                    error: error
                });
            });
    }

    render() {
        const { error, isLoaded } = this.state;
        if (error) {
            return <div>Error: {error.message}</div>;
        } else if (!isLoaded) {
            return <div>Loading...</div>;
        } else {
            const columnNames = this.state.data.statNames;
            const rows = this.state.data.logs;
            const mappedRows = mapMultipleRowsToCol(columnNames, rows);
            const columns = constructReactTableColumns(columnNames, COLUMN_WIDTHS, {}, IGNORE_STATS);

            return (<ReactTable
                className={'-striped -highlight'}
                data={mappedRows}
                columns={columns}
                sortable={false}
                SubComponent={
                    (row) => {
                        return (<TeamBoxScore gameId={row.original.GAME_ID} teamAbbreviation={row.original.TEAM_ABBREVIATION} />);
                    }
                }
                showPagination={false}
                showPageJump={false}
                resizable={false}
                defaultPageSize={MAX_LOGS_PER_PAGE}
                style={PLAYER_LOGS_STYLE}
            />);
        }
    }
}