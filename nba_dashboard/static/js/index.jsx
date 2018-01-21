import React from "react";
import ReactDOM from "react-dom";
import ReactTable from 'react-table'
// import 'react-table/react-table.css'

const TEAM_BOX_SCORE_HEADER_MAP = {
    'TEAM_ABBREVIATION': 'Team',
    'PLAYER_NAME': 'Player',
    'START_POSITION': 'P',
    'PLUS_MINUS': '+/-',
    'FG_PCT': 'FG%',
    'FG3_PCT': 'FG3%',
    'FT_PCT': 'FT%',
    'NBA_TO': 'TOV'
};
const TEAM_BOX_SCORE_IGNORE_STATS = new Set([
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
    'PLAYER_NAME': 120
};

function incrementDateByDays(date, numDays) {
    const copiedDate = new Date(date)
    copiedDate.setDate(copiedDate.getDate() + numDays);
    return copiedDate;
}

/**
 * https://stackoverflow.com/questions/23593052/format-javascript-date-to-yyyy-mm-dd
 * @param {*} date JS Date object
 */
function formatDate(date) {
    var d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2) month = '0' + month;
    if (day.length < 2) day = '0' + day;

    return [year, month, day].join('-');
}

const mapRowToCol = function mapRowToColDictionary(colNames, rowValues) {
    const mapping = {};
    for (let i = 0; i < colNames.length; i += 1) {
        mapping[colNames[i]] = rowValues[i];
    }
    return mapping;
};

const mapMultipleRowsToCol = function mapMultipleRowsToColDictionary(colNames, rows) {
    return rows.map((row) => mapRowToCol(colNames, row));
};

const constructReactTableColumns = function(colNames, columnWidths, mapping, ignoreCols) {
    const reactTableColumns = [];
    colNames.forEach((colName) => {
        if (!(ignoreCols.has(colName))) {
            const colProps = {
                'Header': colName in mapping ? mapping[colName] : colName,
                'accessor': colName,
                'width': columnWidths[colName], // if not in dict, undefined (which is intended)
                'minWidth': undefined
            };
            reactTableColumns.push(colProps);
        }
    });
    return reactTableColumns;
};

class PlayerBoxScoreRow extends React.Component {
    render() {
        const rowValues = this.props.statValues.map((statValue, i) =>
            <td key={i}>{statValue}</td>
        );
        return (
            <tr key={this.props.statValues[0]}>
                {rowValues}
            </tr>
        );
    }
}

class TeamBoxScore extends React.Component {
    render() {
        const columnNames = this.props.statNames;
        const header = this.props.teamName;
        const columns = constructReactTableColumns(columnNames, COLUMN_WIDTHS,
            TEAM_BOX_SCORE_HEADER_MAP, TEAM_BOX_SCORE_IGNORE_STATS);
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
            showPagination={false}
            showPageJump={false}
            defaultPageSize={14}
            style={{
                width: '48%',
                fontSize: '12px',
                float: 'left',
                margin: '10px'
            }}
        />);
    }
}

class GameBoxScore extends React.Component {
    render() {
        const statNames = this.props.game.statNames;
        const playersByTeam = this.props.game.playersByTeam;

        const playingTeams = Object.keys(playersByTeam).map((team) => 
            <TeamBoxScore players={playersByTeam[team]}
                            statNames={statNames}
                            teamName={team}
                            key={team} />
        );

        return (
            <div className={'game-container'} style={{
                    display: 'inline',
                    width: '100%',
                    textAlign: 'center'
                }}>
                {playingTeams}
            </div>
        );
    }
}

class GameDateChanger extends React.Component {
    render() {
        return (<div style={{textAlign: 'center'}}>
            <button
                onClick={(e) => this.props.onDateChange(incrementDateByDays(this.props.date, -1))}
                >{'<'}</button>
            {formatDate(this.props.date)}
            <button
                onClick={(e) => this.props.onDateChange(incrementDateByDays(this.props.date, 1))}
                >{'>'}</button>
        </div>);
    }
}

class BoxScoresContainer extends React.Component {
    constructor(props) {
        super(props);
        const gameDate = incrementDateByDays(new Date(), -1);
        this.state = {
            error: null,
            isLoaded: false,
            games: [],
            date: gameDate
        };
        this.handleDateChange = this.handleDateChange.bind(this);
    }

    componentDidMount() {
        this.handleDateChange(this.state.date);
    }

    handleDateChange(date) {
        this.state.date = date;
        this.fetchGameDateGames(formatDate(date));
    }

    fetchGameDateGames(date) {
        console.log(date);
        fetch('/game_date_games/' + date)
            .then(res => res.json())
            .then(
            (result) => {
                console.log(result);
                this.setState({
                    isLoaded: true,
                    games: result.games
                });
            },
            // Note: it's important to handle errors here
            // instead of a catch() block so that we don't swallow
            // exceptions from actual bugs in components.
            (error) => {
                this.setState({
                    isLoaded: true,
                    error
                });
            }
            );
    }

    render() {
        const { error, isLoaded } = this.state;
        if (error) {
            return <div>Error: {error.message}</div>;
        } else if (!isLoaded) {
            return <div>Loading...</div>;
        } else {
            const gameDateChanger = (<GameDateChanger
                date={this.state.date}
                onDateChange={this.handleDateChange}
            />)

            const teamBoxScores = this.state.games.map((game, i) => 
                <GameBoxScore game={game} key={i} />
            );

            if (teamBoxScores.length == 0) {
                return (
                    <div>
                        {gameDateChanger}
                        <div style={{textAlign: 'center'}}>
                            No data found.
                        </div>
                    </div>
                );
            }
            return (
                <div>
                    {gameDateChanger}
                    <div>
                        {teamBoxScores}
                    </div>
                </div>
            );
        }
    }
}

ReactDOM.render(<BoxScoresContainer />, document.getElementById("content"));
