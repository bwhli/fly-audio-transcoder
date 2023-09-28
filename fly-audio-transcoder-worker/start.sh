#!/bin/sh

# Read API URL and Job ID from the environment.
API_URL="$API_URL"
JOB_ID="$JOB_ID"
echo API URL: ${API_URL}
echo Job ID: ${JOB_ID}

# Fetch job details from the API.
job_json=$(curl -s -X GET "${API_URL}/jobs/${JOB_ID}/")
echo "${job_json}" | jq

# Download the source file.
source_file_download_url=$(echo $job_json | jq -r '.data.source.download_url')
curl -s -X GET "${source_file_download_url}" -o /tmp/${JOB_ID}

# Set .wav file extension for the source file.
# In a production environment that accepts multiple file types,
# there would be additional logic to determine the file type in order to set the correct extension.
mv "/tmp/${JOB_ID}" /tmp/${JOB_ID}.wav
echo Moved "/tmp/${JOB_ID}" to "/tmp/${JOB_ID}.wav"

# Set target format details.
target_extension=$(echo $job_json | jq -r '.data.transcode.format.extension')
target_bit_rate=$(echo $job_json | jq -r '.data.transcode.format.bit_rate')
target_sample_rate=$(echo $job_json | jq -r '.data.transcode.format.sample_rate')
echo Target Format: ${target_extension}, ${target_bit_rate}k, ${target_sample_rate}hz

# Transcode the source file to the target format.
ffmpeg -y -i /tmp/${JOB_ID}.wav -b:a ${target_bit_rate}k -ar ${target_sample_rate} -acodec libmp3lame /tmp/${JOB_ID}.${target_extension}

# Upload the transcoded file to R2.
curl -X PUT \
     -T "/tmp/${JOB_ID}.${target_extension}" \
     -H "Content-Type: audio/mpeg" \
     -H "Content-Disposition: attachment;filename=${JOB_ID}.mp3" \
     "$(echo $job_json | jq -r '.data.transcode.upload_url')"

# Mark job as complete.
completed_job_json=$(curl -X POST "${API_URL}/jobs/${JOB_ID}/status/completed/")
echo "${completed_job_json}" | jq

exit 0