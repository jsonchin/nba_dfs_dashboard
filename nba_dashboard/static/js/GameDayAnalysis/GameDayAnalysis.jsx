import React from 'react'
import { FileUpload } from './FileUpload'
import { GameDayPlayers } from './GameDayPlayers'


export class GameDayAnalysis extends React.Component {
    constructor (props) {
        super(props);

        this.state = {
            data: {},
            isLoaded: false
        }

        this.handleFileUploadDraftKingsPost = this.handleFileUploadDraftKingsPost.bind(this);
    }

    handleFileUploadDraftKingsPost (data) {
        this.setState({
            data: data,
            isLoaded: true
        });
    }

    render() {
        if (this.state.isLoaded) {
            return (
                <div>
                    <div style={{ margin: '50px', width: '20vw', float: 'left' }}>
                        <GameDayPlayers players={this.state.data.matchedPlayers} />
                    </div>
                    <div id={'player-analysis-output'} style={{ margin: '50px', width: '60vw', float: 'left'}}></div>
                </div>);
        } else {
            return (
                <div style={{ margin: '50px' }}>
                    <FileUpload onFileUploadResponse={this.handleFileUploadDraftKingsPost} />
                </div>);
        }
    }
}