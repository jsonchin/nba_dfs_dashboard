import React from "react";
import ReactTable from 'react-table'
import { mapMultipleRowsToCol, constructReactTableColumns, HEADER_MAP } from './utils'

const IGNORE_STATS = new Set([
    'GAME_ID',
    'FTA',
    'FTM',
    'FT_PCT',
    'PF',
    'TEAM_ABBREVIATION',
    'COMMENT',
    'FG3A',
    'FGA'
]);

const COLUMN_WIDTHS = {
    'MIN': 40
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
            const columns = constructReactTableColumns(columnNames, COLUMN_WIDTHS, HEADER_MAP, IGNORE_STATS);

            return (<ReactTable
                className={'-striped -highlight'}
                data={mappedRows}
                columns={columns}
                showPagination={false}
                showPageJump={false}
                defaultPageSize={MAX_LOGS_PER_PAGE}
            />);
        }
    }
}