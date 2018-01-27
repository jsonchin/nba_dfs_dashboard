import React from "react";
import ReactTable from 'react-table'
import { mapMultipleRowsToCol, constructReactTableColumns } from './utils'
import { TeamBoxScore } from './TeamBoxScore'


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
            const columnNames = ['GAME_DATE', 'MATCHUP', 'DK_FP', 'WL', 'MIN', 'PTS', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'DD2', 'TD3', 'FGM', 'FG_PCT', 'FG3M', 'FG3_PCT', 'PLUS_MINUS'];
            const rows = this.state.data.logs;
            const columns = constructReactTableColumns(columnNames, COLUMN_WIDTHS, {}, new Set());

            return (<ReactTable
                className={'-striped -highlight'}
                data={rows}
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