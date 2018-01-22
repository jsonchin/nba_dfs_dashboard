import React from "react";
import ReactTable from 'react-table'
import { mapMultipleRowsToCol, constructReactTableColumns } from './utils'


const IGNORE_STATS = new Set([
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

const PLAYER_AVERAGES_STYLE = {
    width: '100%',
    fontSize: '12px',
    textAlign: 'center'
};

const MAX_LOGS_PER_PAGE = 1;

export class PlayerAverages extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            error: null,
            isLoaded: false,
            data: null
        };

        fetch('/player/' + this.props.playerId + '/averages')
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
            const row = this.state.data.averages;
            const rows = [row];
            const mappedRows = mapMultipleRowsToCol(columnNames, rows);
            const columns = constructReactTableColumns(columnNames, COLUMN_WIDTHS, {}, IGNORE_STATS);

            return (<ReactTable
                className={'-striped -highlight'}
                data={mappedRows}
                columns={columns}
                sortable={false}
                resizable={false}
                showPagination={false}
                showPageJump={false}
                defaultPageSize={MAX_LOGS_PER_PAGE}
                style={PLAYER_AVERAGES_STYLE}
            />);
        }
    }
}