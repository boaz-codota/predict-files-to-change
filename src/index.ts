import * as core from "@actions/core";
import { context, getOctokit } from "@actions/github";

async function run() {
  try {
    const token = core.getInput('github-token', {required: true})
    
    // FIXME: DELETE ME
    core.info(`Received token with length: "${token.length}"`)

    const client = getOctokit(token)

    const issue = await getIssue(client)
    core.info(`Making a prediction of file for issue titled: "${issue.title}"`)
    core.info(`Issue content: \n---\n${issue.body}\n---\n`)
    client.issues.createComment({
      ...context.repo,
      issue_number: issue.issue_number,
      body: 'Kaki pipi `23`'
    })
  } catch (error) {
    core.setFailed(error.message)
  }
}

async function getIssue(
  client: any
): Promise<{title: string; body: string; issue_number: number}> {
  const issue_number = context.payload.issue?.number

  const {data} = await client.issues.get({
    ...context.repo,
    issue_number
  })

  return {issue_number, ...data}
}

run();
