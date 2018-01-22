import React from "react";
import { TeamBoxScore } from '../TeamBoxScore'


const GAME_CONTAINER_STYLE = {
    display: 'flex',
    justifyContent: 'center',
    width: '100%'
};

const GAME_TEAM_BOX_SCORE_STYLE = {
    width: '48%',
    margin: '10px'
};

export class GameBoxScore extends React.Component {
    render() {
        const playingTeams = this.props.teamAbbreviations.map((teamAbbreviation) =>
            <TeamBoxScore gameId={this.props.gameId} teamAbbreviation={teamAbbreviation}
                key={teamAbbreviation} />
        );

        return (
            <div className={'game-container'} style={GAME_CONTAINER_STYLE}>
                <div style={GAME_TEAM_BOX_SCORE_STYLE}>
                    {playingTeams[0]}
                </div>

                <div style={GAME_TEAM_BOX_SCORE_STYLE}>
                    {playingTeams[1]}
                </div>
            </div>
        );
    }
}
