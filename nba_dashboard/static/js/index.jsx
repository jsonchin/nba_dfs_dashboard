import React from "react";
import ReactDOM from "react-dom";


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
        const playerRows = this.props.players.map((player) => 
            <PlayerBoxScoreRow statValues={player} key={player[0]} />
        );

        const statNamesHeaders = this.props.statNames.map((statName) =>
            <th key={statName}>{statName}</th>
        );

        return (<table className="table">
            <thead>
                <tr>{statNamesHeaders}</tr>
            </thead>
            <tbody>
                {playerRows}
            </tbody>
        </table>);
    }
}

class GameBoxScore extends React.Component {
    render() {
        const statNames = this.props.game.statNames;
        const playersByTeam = this.props.game.playersByTeam;

        const playingTeams = Object.keys(playersByTeam).map((team) => 
            <TeamBoxScore players={playersByTeam[team]} statNames={statNames} key={team} />
        );

        return (
            <div>
                {playingTeams}
            </div>
        );
    }
}

class BoxScoresContainer extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            error: null,
            isLoaded: false,
            games: []
        };
    }

    componentDidMount() {
        fetch("/game_date_games/2018-01-19")
            .then(res => res.json())
            .then(
            (result) => {
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
            )
    }

    render() {
        const { error, isLoaded, items } = this.state;
        if (error) {
            return <div>Error: {error.message}</div>;
        } else if (!isLoaded) {
            return <div>Loading...</div>;
        } else {
            const teamBoxScores = this.state.games.map((game, i) => 
                teamBoxScores.push(<GameBoxScore game={game} key={i} />)
            );

            if (teamBoxScores.length == 0) {
                return (<div>
                    No data found.
                </div>)
            }

            return (<div>
                {teamBoxScores}
            </div>);
        }
    }
}

ReactDOM.render(<BoxScoresContainer />, document.getElementById("content"));
