import React from "react";
import { PlayerAverages } from './PlayerAverages'


export class PlayerProfile extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            error: null,
            isLoaded: false,
            data: null
        };

        fetch('/player/' + this.props.playerId + '/profile')
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
            const names = this.state.data.name.split(' ');
            const firstName = names[0];
            const lastName = names.slice(1).join(' ');
            return (<div style={{ width: '100%' }}>
                <div>
                    <img src={this.state.data.pictureUrl} style={{ float: 'left' }} />
                </div>
                <div style={{ textAlign: 'left', fontFamily: 'Roboto Condensed',
                                display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                    <p style={{ fontSize: '24px', margin: 0, lineHeight: '28px' }}>{firstName}</p>
                    <p style={{ fontSize: '24px', margin: 0, lineHeight: '28px', fontWeight: 'bold' }}>{lastName}</p>
                    <h4>{this.state.data.position} {'|'} {this.state.data.team}</h4>
                    <PlayerAverages playerId={this.props.playerId} />
                </div>
            </div>);
        }
    }
}