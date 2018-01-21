import React from "react";
import ReactTable from 'react-table'
import { GameBoxScore } from './GameBoxScore'


/**
 * Non destructively returns the incremented date.
 * @param {Date} date A Javascript Date object.
 * @param {integer} numDays The number of days to increment (can be pos or neg).
 */
function incrementDateByDays(date, numDays) {
    const copiedDate = new Date(date)
    copiedDate.setDate(copiedDate.getDate() + numDays);
    return copiedDate;
}

/**
 * Formats a Javascript Date object in YYYY-MM-DD form with 0 padding.
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


class GameDateChanger extends React.Component {
    render() {
        return (<div style={{ textAlign: 'center' }}>
            <button
                className={'btn btn-outline-secondary'}
                onClick={(e) => this.props.onDateChange(incrementDateByDays(this.props.date, -1))}
            >{'<'}</button>
            <span style={{margin: 10}}><b>{formatDate(this.props.date)}</b></span>
            <button
                className={'btn btn-outline-secondary'}
                onClick={(e) => this.props.onDateChange(incrementDateByDays(this.props.date, 1))}
            >{'>'}</button>
        </div>);
    }
}

export class GameDateGames extends React.Component {
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
                    error: error
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
                        <div style={{ textAlign: 'center' }}>
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

