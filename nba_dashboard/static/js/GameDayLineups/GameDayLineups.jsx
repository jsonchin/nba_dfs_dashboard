import React from 'react'
import ReactDOM from "react-dom";
import ReactTable from 'react-table'
import { PlayerProfile } from '../PlayerProfile'
import { PlayerLogs } from '../PlayerLogs'


const MATCHUP_STYLE = {
    margin: '10px',
    display: 'inline-block'
};
const LINEUP_STYLE = {
    fontSize: '12px',
    textAlign: 'center',
    float: 'left'
};
const MAX_PLAYERS_PER_LINEUP = 12;

class GameDayLineup extends React.Component {
    render () {
        return (
            <ReactTable
                className={'-highlight'}
                data={this.props.players}
                columns={[
                    {
                        Header: () => <span><b>{this.props.team}</b></span>,
                        columns: [
                            {
                                'id': 'Player+Position',
                                'accessor': (row) => {
                                    return row.name + (row.position != '' ? (' (' + row.position + ')') : '');
                                },
                                'width': 140,
                                'minWidth': undefined
                            }
                        ]
                    }
                ]}
                getTrProps={(state, rowInfo) => {
                    return {
                        style: {
                            background: rowInfo.original.position == '' ? '' : '#f6f6f6',
                            height: '30px'
                        },
                        onClick: (e) => {
                            ReactDOM.unmountComponentAtNode(document.getElementById('lineup-analysis-output'));
                            ReactDOM.render(
                                <div>
                                    <PlayerProfile playerId={rowInfo.original.playerId} />
                                    <PlayerLogs playerId={rowInfo.original.playerId} />
                                </div>,
                                document.getElementById('lineup-analysis-output')
                            );
                        }
                    }
                }}
                showPagination={false}
                showPageJump={false}
                sortable={false}
                defaultPageSize={MAX_PLAYERS_PER_LINEUP}
                style={LINEUP_STYLE}
            />
        );
    }
}

export class GameDayLineups extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            error: null,
            isLoaded: false,
            data: null
        };

        fetch('/lineups')
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
            const lineupsByTeam = this.state.data.lineups;
            const matchups = this.state.data.matchups;

            const lineupMatchupTables = matchups.map((matchup) => {
                const team1 = matchup[0];
                const team2 = matchup[1];
                const players1 = lineupsByTeam[team1];
                const players2 = lineupsByTeam[team2];

                return (
                    <div className={'matchup-lineups'} key={team1 + ' @ ' + team2} style={MATCHUP_STYLE}>
                        <GameDayLineup players={players1} team={team1} />
                        <GameDayLineup players={players2} team={'@' + team2} />
                    </div>
                );
            });

            return (
                <div style={{ textAlign: 'center', display: 'inline-block'
                }}>
                    <div style={{ width: '100vw', display: 'inline-block', textAlign: 'center' }}>
                        {lineupMatchupTables}
                    </div>
                    <div id={'lineup-analysis-output'} style={{ margin: '10px', width: '45vw', display: 'inline-block' }}></div>
                </div>
            );
        }
    }
}