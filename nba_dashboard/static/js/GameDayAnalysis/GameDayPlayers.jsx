import React from 'react'
import ReactDOM from "react-dom";
import ReactTable from 'react-table'
import { constructReactTableColumns } from '../utils'
import { PlayerProfile } from '../PlayerProfile'
import { PlayerLogs } from '../PlayerLogs'


const headerMapping = {
    'matchedName': 'Player',
    'salary': 'Salary',
    'formattedNBAMatchup': 'Matchup',
    'team': 'Team',
    'opponentTeam': 'Opp',
    'position': 'P'
};

const columnWidths = {
    'matchedName': 120,
    'formattedNBAMatchup': 90,
    'position': 50
};

const gameDayPlayersStyle = {
    fontSize: '12px',
    textAlign: 'center',
    height: '90vh'
};


export class GameDayPlayers extends React.Component {
    render() {
        const colNames = ['matchedName', 'formattedNBAMatchup', 'position', 'salary'];
        const columns = constructReactTableColumns(colNames, columnWidths, headerMapping, new Set());

        return (<ReactTable
            data={this.props.players}
            columns={columns}
            getTrProps={(state, rowInfo) => {
                return {
                    onClick: (e) => {
                        ReactDOM.unmountComponentAtNode(document.getElementById('player-analysis-output'));
                        ReactDOM.render(
                            <div>
                                <PlayerProfile playerId={rowInfo.original.matchedPlayerId} />
                                <PlayerLogs playerId={rowInfo.original.matchedPlayerId} />
                            </div>,
                            document.getElementById('player-analysis-output')
                        );
                    }
                }
            }}
            defaultPageSize={this.props.players.length}
            showPagination={false}
            showPageJump={false}
            style={gameDayPlayersStyle}
        />);
    }
}