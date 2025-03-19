import { execSync } from "node:child_process"

// Typdefinitionen für Serverless
interface ServerlessInstance {
  service: {
    provider: {
      stage: string
      environment: Record<string, string>
      iam?: {
        role: {
          statements: Array<{
            Effect: string
            Action: string[]
            Resource: string
          }>
        }
      }
      [key: string]: any
    }
    custom?: Record<string, any>
    layers?: Record<string, any>
    functions: Record<string, any>
    package?: Record<string, any>
  }
  configurationInput: {
    provider: Record<string, any>
  }
}

interface ServerlessOptions {
  stage?: string
  [key: string]: any
}

async function execCommand(command: string, args: string): Promise<string> {
  return await execSync(`${command} ${args}`).toString().trim()

  const process = new Deno.Command(command, {
    args: args.split(" "),
    stdout: "piped",
    stderr: "piped",
  }).spawn()

  const { stdout, stderr } = await process.output()

  if (stderr) {
    const errorOutput = new TextDecoder().decode(stderr).trim()
    throw new Error(`Command failed: ${errorOutput}`)
  }
  return new TextDecoder().decode(stdout).trim()
}

class ServerlessDefault {
  static tags = ["build"]

  private serverless: ServerlessInstance
  private options: ServerlessOptions
  private stage: string
  private hooks: Record<string, () => void>

  constructor(serverless: ServerlessInstance, options: ServerlessOptions) {
    this.serverless = serverless
    this.options = options
    this.stage = this.options["stage"] || this.serverless.service.provider.stage
    this.serverless.service.provider.stage = this.options["stage"] || "dev"
    this.hooks = {
      initialize: () => this.init(),
      //'before:package:package': () => this.beforePackage(),
    }
  }

  async setEnvFromSSM(ssmName: string, envName: string): Promise<void> {
    try {
      const args = `ssm get-parameter --name ${ssmName} --with-decryption --query Parameter.Value`
      let output = await execCommand("aws", args)
      output = output.replace(/^"|"$/g, "")
      this.serverless.service.provider.environment[envName] = output
    } catch (error) {
      console.log(`Error retrieving SSM parameter ${ssmName}:`, error)
    }
  }

  async init(): Promise<void> {
    this.setCustomConfig()
    this.setProviderConfig()
    this.setPackageConfig()

    // set environment variables from SSM
    this.serverless.service.provider.environment[
      "TES_DB_URI"
    ] = `\${ssm:/TES_DB_URI-${this.stage}~true}`

    //await this.setEnvFromSSM(`TES_DB_URI-${this.stage}`, "TES_DB_URI")
    this.setFunctionDefaults()
  }

  setCustomConfig(): void {
    const customConfig = this.serverless.service.custom || {}
    customConfig.logLevel = { prod: "INFO", default: "DEBUG" }
    //customConfig.tesBase = 'arn:aws:lambda:eu-central-1:495963541969:function:sls-tes-webhook-dev'
    customConfig.basePath = { dev: "dev", prod: "" }
    customConfig.provisionedConcurrency = { dev: 0, prod: 0 }
    customConfig.lambdaInsights = { defaultLambdaInsights: true }

    if (customConfig.customDomain?.rest) {
      const basePath = customConfig.basePath[this.stage]
      customConfig.customDomain.rest.basePath = basePath
      customConfig.customDomain.rest.createRoute53Record = true
      customConfig.customDomain.rest.apiType = "http"
      customConfig.customDomain.rest.endpointType = "edge"
      customConfig.customDomain.rest.autoDomain = false
    }

    customConfig.defaultCors = {
      origin: "*",
      headers: [
        "Content-Type",
        "X-Amz-Date",
        "Authorization",
        "X-Api-Key",
        "X-Amz-Security-Token",
        "X-Amz-User-Agent",
        "X-Amzn-Trace-Id",
        "m-g-session",
        "M-G-Session",
        "m-profile",
        "M-Profile",
      ],
      allowCredentials: true,
    }
    customConfig.pythonRequirements = {
      layer: true,
      strip: true,
      slim: true,
      useDownloadCache: true,
      useStaticCache: true,
      invalidateCaches: true,
      pipCmdExtraArgs: [
        "--platform=manylinux2014_x86_64",
        "--only-binary=:all:",
      ],
    }
  }

  setProviderConfig(): void {
    const providerConfig = this.serverless.service.provider || {}
    const inputConfig = this.serverless.configurationInput.provider
    providerConfig.deploymentBucket = "kinayu--serverless-deployments"
    providerConfig.deploymentBucketObject = {
      name: "kinayu--serverless-deployments",
    }
    if (!inputConfig.runtime) {
      providerConfig.runtime = "python3.13"
    }
    if (!inputConfig.memorySize) {
      providerConfig.memorySize = 1536
    }
    if (!inputConfig.architecture) {
      providerConfig.architecture = "arm64"
    }
    if (!inputConfig.timeout) {
      providerConfig.timeout = 20
    }
    providerConfig.deploymentMethod = "direct"
    providerConfig.versionFunctions = false
    providerConfig.logRetentionInDays = 14
    providerConfig.environment = providerConfig.environment || {}
    providerConfig.environment.stage = this.options.stage || "dev"
    providerConfig.environment.LOGLEVEL = "DEBUG"
    providerConfig.apiGateway = {
      apiKeySourceType: "HEADER",
      minimumCompressionSize: 1024,
    }

    if (!this.serverless.service.provider.iam) {
      this.serverless.service.provider.iam = { role: { statements: [] } }
    }
    this.serverless.service.provider.iam.role.statements = [
      {
        Effect: "Allow",
        Action: ["xray:PutTraceSegments", "xray:PutTelemetryRecords"],
        Resource: "*",
      },
    ]

    providerConfig.layers = providerConfig.layers || []
    providerConfig.layers.push({
      Ref: "PythonRequirementsLambdaLayer",
    })
  }

  setPackageConfig(): void {
    const packageConfig = this.serverless.service.package || {}
    packageConfig.excludeDevDependencies = true
    packageConfig.patterns = [
      "!bin",
      "!venv",
      "!node_modules",
      "!yml",
      "!package*",
      "!pyproject.toml",
      "!requirements*",
      "!LICENSE",
      "!README*",
      "!test*",
      "!.*",
    ]
  }

  setFunctionDefaults(): void {
    const functionConfig = this.serverless.service.functions
    const customConfig = this.serverless.service.custom
    if (!customConfig) {
      throw new Error("Custom config not set")
    }

    // loop over functions
    for (const functionName in functionConfig) {
      // set default function settings
      for (let event in functionConfig[functionName].events) {
        functionConfig[functionName].events[event].cors =
          customConfig.defaultCors
      }
      const provisionedConcurrency =
        customConfig.provisionedConcurrency[this.stage] || 0
      functionConfig[functionName].provisionedConcurrency =
        provisionedConcurrency
    }
  }
}

// Deno-kompatibler Export
export default ServerlessDefault
