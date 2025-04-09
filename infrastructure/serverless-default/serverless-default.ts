import { execSync } from "node:child_process"
import path from "node:path"
import { randomBytes } from "node:crypto"

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
    resources?: Record<string, any>
  }
  cli: {
    consoleLog: (message: string) => void
    log: (message: string) => void
    logError: (message: string) => void
    logWarning: (message: string) => void
    logSuccess: (message: string) => void
    logInfo: (message: string) => void
    logDebug: (message: string) => void
    logVerbose: (message: string) => void
  }
  configurationInput: {
    provider: Record<string, any>
  }
  getProvider: (providerName: string) => any
}

interface CloudFrontInvalidateConfig {
  stage?: string
  distributionId: string
  distributionIdKey?: string
  autoInvalidate?: boolean
  items: string[]
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
  private provider: string
  private aws: any

  constructor(serverless: ServerlessInstance, options: ServerlessOptions) {
    this.serverless = serverless
    this.options = options
    this.stage = this.options["stage"] || this.serverless.service.provider.stage
    this.serverless.service.provider.stage = this.options["stage"] || "dev"
    this.provider = "aws"
    this.aws = this.serverless.getProvider("aws")

    this.hooks = {
      initialize: () => this.init(),
      "after:deploy:deploy": this.afterDeploy.bind(this),
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

    await this.setEnvFromSSM(`TES_DB_URI-${this.stage}`, "TES_DB_URI")
    this.setFunctionDefaults()
    this.setResources()
  }

  setCustomConfig(): void {
    const customConfig = this.serverless.service.custom || {}
    customConfig.logLevel = { prod: "INFO", default: "DEBUG" }
    //customConfig.tesBase = 'arn:aws:lambda:eu-central-1:495963541969:function:sls-tes-webhook-dev'
    customConfig.basePath = { dev: "dev", prod: "" }
    customConfig.provisionedConcurrency = { dev: 0, prod: 0 }
    customConfig.lambdaInsights = { defaultLambdaInsights: true }

    if (customConfig.tes?.type === "frontend") {
      const customerCode = customConfig.tes.customerCode
      const customerName = customConfig.tes.customerName
      const projectName = customConfig.tes.projectName
      customConfig.s3bucket = `${customerCode}-${customerName}/${projectName}/${this.stage}`

      customConfig.assets = {
        auto: true,
        targets: [
          {
            bucket: "frontend--websites",
            empty: true,
            prefix: customConfig.s3bucket,
            files: [
              {
                source: ".output/public/",
                globs: "**/**",
                headers: {
                  CacheControl: "no-cache",
                },
              },
            ],
          },
        ],
      }

      customConfig.certificate = {
        dev: "arn:aws:acm:us-east-1:495963541969:certificate/5976467c-2761-4293-a0df-ed47f8c33b3b",
        test: "arn:aws:acm:us-east-1:495963541969:certificate/5976467c-2761-4293-a0df-ed47f8c33b3b",
        prod:
          customConfig.tes.prod?.certificate ||
          "arn:aws:acm:us-east-1:495963541969:certificate/5976467c-2761-4293-a0df-ed47f8c33b3b",
      }

      customConfig.aliases = {
        dev: `dev-${customerCode}-${projectName}.4pd3v.com`,
        test: `test-${customerCode}-${projectName}.4pd3v.com`,
        prod:
          customConfig.tes.prod?.alias ||
          `live-${customerCode}-${projectName}.4pd3v.com`,
      }

      customConfig.cloudfrontInvalidate = {
        distributionIdKey: "CDNDistributionId",
        autoInvalidate: true,
        items: ["/*"],
      }
    } else {
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
          "--platform=manylinux2014_aarch64",
          "--only-binary=:all:",
        ],
      }
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

    /*

    providerConfig.layers = providerConfig.layers || []
    providerConfig.layers.push({
      "!Ref": "PythonRequirementsLambdaLayer",
    })
      */
  }

  setPackageConfig(): void {
    const packageConfig = this.serverless.service.package || {}
    const customConfig = this.serverless.service.custom || {}

    packageConfig.excludeDevDependencies = true
    if (customConfig.tes?.type === "frontend") {
      packageConfig.patterns = ["!**", ".output/server/**"]
    } else {
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
  }

  setFunctionDefaults(): void {
    const functionConfig = this.serverless.service.functions
    const customConfig = this.serverless.service.custom
    if (!customConfig) {
      throw new Error("Custom config not set")
    }

    if (customConfig.tes?.type === "frontend") {
      functionConfig["cfOriginRequest"] = {
        handler: ".output/server/index.handler",
        events: [
          {
            http: {
              method: "GET",
              path: "/",
              cors: true,
            },
          },
          {
            http: {
              method: "GET",
              path: "/{proxy+}",
              cors: true,
            },
          },
        ],
      }
    } else {
      // loop over functions
      for (const functionName in functionConfig) {
        // set default function settings
        for (let event in functionConfig[functionName].events) {
          for (let key in functionConfig[functionName].events[event]) {
            if (key === "http" || key === "httpApi") {
              functionConfig[functionName].events[event][key].cors =
                customConfig.defaultCors
            }
          }
        }
        /*
        const provisionedConcurrency =
          customConfig.provisionedConcurrency[this.stage] || 0
        functionConfig[functionName].provisionedConcurrency =
          provisionedConcurrency
          */
        functionConfig[functionName].layers =
          functionConfig[functionName].layers || []
        functionConfig[functionName].layers.push({
          Ref: "PythonRequirementsLambdaLayer",
        })
      }
    }
  }

  setResources(): void {
    const customConfig = this.serverless.service.custom || {}
    const resourcesConfig = this.serverless.service.resources || {}

    if (customConfig.tes?.type === "frontend") {
      resourcesConfig.Resources = resourcesConfig.Resources || {}
      ;(resourcesConfig.Resources.CloudFrontDistribution = {
        Type: "AWS::CloudFront::Distribution",
        Properties: {
          DistributionConfig: {
            Aliases: [customConfig.aliases[this.stage]],
            Origins: [
              {
                Id: "static",
                DomainName:
                  "frontend--websites.s3-website.eu-central-1.amazonaws.com",
                OriginPath: `/${customConfig.s3bucket}`,
                ConnectionAttempts: 3,
                ConnectionTimeout: 10,
                CustomOriginConfig: {
                  HTTPPort: 80,
                  HTTPSPort: 443,
                  OriginProtocolPolicy: "http-only",
                },
              },
              {
                Id: "ssr",
                DomainName: {
                  "Fn::Sub":
                    "${ApiGatewayRestApi}.execute-api.${AWS::Region}.amazonaws.com",
                },
                OriginPath: `/${customConfig.basePath[this.stage]}`,
                CustomOriginConfig: {
                  HTTPSPort: 443,
                  OriginProtocolPolicy: "https-only",
                  OriginSSLProtocols: ["TLSv1.2"],
                },
              },
            ],
            CacheBehaviors: [
              {
                PathPattern: "/_nuxt/*",
                AllowedMethods: ["GET", "HEAD", "OPTIONS"],
                TargetOriginId: "static",
                CachePolicyId: "658327ea-f89d-4fab-a63d-7e88639e58f6", // CachingOptimized
                ViewerProtocolPolicy: "redirect-to-https",
                ResponseHeadersPolicyId: "67f7725c-6f97-4210-82d7-5512b31e9d03", // SecurityHeadersPolicy
                Compress: true,
              },
              {
                PathPattern: "/favicon.ico",
                AllowedMethods: ["GET", "HEAD", "OPTIONS"],
                TargetOriginId: "static",
                CachePolicyId: "658327ea-f89d-4fab-a63d-7e88639e58f6", // CachingOptimized
                ViewerProtocolPolicy: "redirect-to-https",
                ResponseHeadersPolicyId: "67f7725c-6f97-4210-82d7-5512b31e9d03", // SecurityHeadersPolicy
                Compress: true,
              },
              {
                PathPattern: "/static/*",
                AllowedMethods: ["GET", "HEAD", "OPTIONS"],
                TargetOriginId: "static",
                CachePolicyId: "658327ea-f89d-4fab-a63d-7e88639e58f6", // CachingOptimized
                ViewerProtocolPolicy: "redirect-to-https",
                ResponseHeadersPolicyId: "67f7725c-6f97-4210-82d7-5512b31e9d03", // SecurityHeadersPolicy
                Compress: true,
              },
            ],
            DefaultCacheBehavior: {
              AllowedMethods: ["GET", "HEAD", "OPTIONS"],
              TargetOriginId: "ssr",
              CachePolicyId: "658327ea-f89d-4fab-a63d-7e88639e58f6", // CachingOptimized
              ViewerProtocolPolicy: "redirect-to-https",
              ResponseHeadersPolicyId: "67f7725c-6f97-4210-82d7-5512b31e9d03", // SecurityHeadersPolicy
            },
            CustomErrorResponses: [
              {
                ErrorCachingMinTTL: 86400, // cache errors for 24h
                ErrorCode: 403, // object not found in bucket
                ResponseCode: 404,
                ResponsePagePath: "/404",
              },
              {
                ErrorCachingMinTTL: 86400, // cache errors for 24h
                ErrorCode: 404, // object not found in bucket
                ResponseCode: 404,
                ResponsePagePath: "/404",
              },
            ],
            Comment: customConfig.s3bucket,
            PriceClass: "PriceClass_100",
            Enabled: true,
            ViewerCertificate: {
              AcmCertificateArn: customConfig.certificate[this.stage],
              SslSupportMethod: "sni-only",
              MinimumProtocolVersion: "TLSv1.2_2021",
            },
            HttpVersion: "http2and3",
          },
        },
      }),
        (resourcesConfig.Outputs = resourcesConfig.Outputs || {})
      resourcesConfig.Outputs.CDNDistributionId = {
        Description: "CloudFront Distribution ID",
        Value: {
          "Fn::GetAtt": ["CloudFrontDistribution", "Id"],
        },
      }
    }
  }

  generateSecureRandomString(length: number): string {
    return randomBytes(Math.ceil(length / 2))
      .toString("hex")
      .slice(0, length)
  }

  colorYellow(text: string): string {
    return `\x1b[33m${text}\x1b[0m`
  }

  createInvalidation(
    distributionId: string,
    reference: string,
    cloudfrontInvalidate: CloudFrontInvalidateConfig
  ): void {
    const cli = this.serverless.cli
    const cloudfrontInvalidateItems = cloudfrontInvalidate.items

    const params = {
      DistributionId: distributionId /* required */,
      InvalidationBatch: {
        /* required */ CallerReference: reference /* required */,
        Paths: {
          /* required */
          Quantity: cloudfrontInvalidateItems.length /* required */,
          Items: cloudfrontInvalidateItems,
        },
      },
    }
    return this.aws.request("CloudFront", "createInvalidation", params).then(
      () => {
        cli.consoleLog(
          `CloudfrontInvalidate: ${this.colorYellow("Invalidation started")}`
        )
      },
      (err: any) => {
        cli.consoleLog(JSON.stringify(err))
        cli.consoleLog(
          `CloudfrontInvalidate: ${this.colorYellow("Invalidation failed")}`
        )
        throw err
      }
    )
  }

  invalidateElements(
    elements: CloudFrontInvalidateConfig[]
  ): Promise<any[]> | undefined {
    const cli = this.serverless.cli

    if (this.options.noDeploy) {
      cli.consoleLog("skipping invalidation due to noDeploy option")
      return
    }

    const invalidationPromises = elements.map((element) => {
      const cloudfrontInvalidate = element
      const reference = this.generateSecureRandomString(16)
      const stage = cloudfrontInvalidate.stage
      let distributionId = cloudfrontInvalidate.distributionId

      if (
        stage !== undefined &&
        stage !== `${this.serverless.service.provider.stage}`
      ) {
        return
      }

      if (distributionId) {
        cli.consoleLog(`DistributionId: ${this.colorYellow(distributionId)}`)

        return this.createInvalidation(
          distributionId,
          reference,
          cloudfrontInvalidate
        )
      }

      if (!cloudfrontInvalidate.distributionIdKey) {
        cli.consoleLog("distributionId or distributionIdKey is required")
        return
      }

      cli.consoleLog(
        `DistributionIdKey: ${this.colorYellow(
          cloudfrontInvalidate.distributionIdKey
        )}`
      )

      // get the id from the output of stack.
      const stackName = this.serverless.getProvider("aws").naming.getStackName()

      return this.aws
        .request("CloudFormation", "describeStacks", { StackName: stackName })
        .then(
          (result: {
            Stacks: { Outputs: { OutputKey: string; OutputValue: string }[] }[]
          }) => {
            if (result) {
              const outputs = result.Stacks[0].Outputs
              outputs.forEach((output) => {
                if (
                  output.OutputKey === cloudfrontInvalidate.distributionIdKey
                ) {
                  distributionId = output.OutputValue
                }
              })
            }
          }
        )
        .then(() =>
          this.createInvalidation(
            distributionId,
            reference,
            cloudfrontInvalidate
          )
        )
        .catch(() => {
          cli.consoleLog(
            "Failed to get DistributionId from stack output. Please check your serverless template."
          )
        })
    })

    return Promise.all(invalidationPromises)
  }

  afterDeploy(): Promise<any[]> | undefined {
    const customConfig = this.serverless.service.custom || {}
    const elementsToInvalidate = customConfig.cloudfrontInvalidate.filter(
      (element: {
        autoInvalidate?: boolean
        distributionId?: string
        distributionIdKey?: string
      }) => {
        if (element.autoInvalidate !== false) {
          return true
        }

        this.serverless.cli.consoleLog(
          `Will skip invalidation for the distributionId "${
            element.distributionId || element.distributionIdKey
          }" as autoInvalidate is set to false.`
        )
        return false
      }
    )

    return this.invalidateElements(elementsToInvalidate)
  }
}

// Deno-kompatibler Export
export default ServerlessDefault
