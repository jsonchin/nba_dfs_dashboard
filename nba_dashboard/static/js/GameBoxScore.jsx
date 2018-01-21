import React from "react";
import { TeamBoxScore } from './TeamBoxScore'


const GAME_CONTAINER_STYLE = {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'baseline',
    width: '100%'
};

export class GameBoxScore extends React.Component {
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
            <div className={'game-container'} style={GAME_CONTAINER_STYLE}>
                {playingTeams}
            </div>
        );
    }
}
