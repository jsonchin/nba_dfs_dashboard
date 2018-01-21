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
    width: '100%',
    fontSize: '12px',
    float: 'left',
    textAlign: 'center'
};

export class TeamBoxScore extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            error: null,
            isLoaded: false,
            data: null
        };

        fetch('/game/' + this.props.gameId + '/' + this.props.teamAbbreviation)
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
            const header = this.props.teamAbbreviation;
            const columns = constructReactTableColumns(columnNames, COLUMN_WIDTHS, HEADER_MAP, IGNORE_STATS);
            const mappedRows = mapMultipleRowsToCol(columnNames, this.state.data.players);
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
}
