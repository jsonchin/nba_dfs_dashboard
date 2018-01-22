import React from 'react'
import axios, { post } from 'axios';

export class FileUpload extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            file: null
        }
        this.onFormSubmit = this.onFormSubmit.bind(this)
        this.onChange = this.onChange.bind(this)
        this.fileUpload = this.fileUpload.bind(this)
    }

    onFormSubmit(e) {
        e.preventDefault() // Stop form submit
        this.fileUpload(this.state.file)
            .then((result) => {
                this.props.onFileUploadResponse(result.data);
            });
    }

    onChange(e) {
        this.setState({ file: e.target.files[0] })
    }
    
    fileUpload(file) {
        const url = '/file_upload/draftkings';
        const formData = new FormData();
        formData.append('file', file)
        const config = {
            headers: {
                'content-type': 'multipart/form-data'
            }
        }
        return post(url, formData, config)
    }

    render() {
        return (
            <form onSubmit={this.onFormSubmit}>
                <h5>Draftkings CSV</h5>
                <input type="file" onChange={this.onChange} />
                <button type="submit">Upload</button>
            </form>
        )
    }
}
