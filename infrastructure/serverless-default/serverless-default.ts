import { execSync } from "node:child_process"
import path from "node:path"
import { randomBytes } from "node:crypto"

// Typdefinitionen für Serverless
interface ServerlessInstance {
  service: {
    service: string
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

// ------ S3 Bucket --------
interface StackResource {
  LogicalResourceId?: string
  PhysicalResourceId?: string
  [key: string]: any
}

interface BucketReference {
  Ref: string
}

interface S3ListObjectsResponse {
  Contents: { Key: string }[]
  IsTruncated: boolean
}

interface AssetFile {
  source: string
  globs: string
  defaultContentType?: string
  headers?: Record<string, any>
}

interface AssetSet {
  bucket: string | BucketReference
  prefix?: string
  empty?: boolean
  acl?: string
  files: AssetFile[]
}

interface S3Config {
  targets: AssetSet[]
  uploadConcurrency: number
  resolveReferences?: boolean
}

/**
 * Options for file globbing
 */
interface GlobOptions {
  cwd?: string
  nodir?: boolean
  dot?: boolean
}

// ------------------------

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
  private aws: any
  private provider: any
  private providerConfig: any
  private custom: any
  private commands: any

  constructor(serverless: ServerlessInstance, options: ServerlessOptions) {
    this.serverless = serverless
    this.options = options
    this.stage = this.options["stage"] || this.serverless.service.provider.stage
    this.serverless.service.provider.stage = this.options["stage"] || "dev"
    this.provider = this.serverless.getProvider("aws")
    this.custom = this.serverless.service.custom || {}
    this.providerConfig = this.serverless.service.provider || {}

    this.hooks = {
      initialize: this.init.bind(this),
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
    this.custom.logLevel = { prod: "INFO", default: "DEBUG" }
    //this.custom.tesBase = 'arn:aws:lambda:eu-central-1:495963541969:function:sls-tes-webhook-dev'
    this.custom.basePath = { dev: "dev", prod: "" }
    this.custom.provisionedConcurrency = { dev: 0, prod: 0 }
    this.custom.lambdaInsights = { defaultLambdaInsights: true }

    if (this.custom.tes?.type === "frontend") {
      const customerCode = this.custom.tes.customerCode
      const customerName = this.custom.tes.customerName
      const projectName = this.custom.tes.projectName
      this.custom.s3bucket = `${customerCode}-${customerName}/${projectName}/${this.stage}`

      this.custom.assets = {
        auto: true,
        targets: [
          {
            bucket: "frontend--websites",
            empty: true,
            prefix: this.custom.s3bucket,
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

      this.custom.certificate = {
        dev: "arn:aws:acm:us-east-1:495963541969:certificate/5976467c-2761-4293-a0df-ed47f8c33b3b",
        test: "arn:aws:acm:us-east-1:495963541969:certificate/5976467c-2761-4293-a0df-ed47f8c33b3b",
        prod:
          this.custom.tes.prod?.certificate ||
          "arn:aws:acm:us-east-1:495963541969:certificate/5976467c-2761-4293-a0df-ed47f8c33b3b",
      }

      this.custom.aliases = {
        dev: `dev-${customerCode}-${projectName}.4pd3v.com`,
        test: `test-${customerCode}-${projectName}.4pd3v.com`,
        prod:
          this.custom.tes.prod?.alias ||
          `live-${customerCode}-${projectName}.4pd3v.com`,
      }

      this.custom.cloudfrontInvalidate = {
        distributionIdKey: "CDNDistributionId",
        autoInvalidate: true,
        items: ["/*"],
      }
    } else {
      if (this.custom.customDomain?.rest) {
        const basePath = this.custom.basePath[this.stage]
        this.custom.customDomain.rest.basePath = basePath
        this.custom.customDomain.rest.createRoute53Record = true
        this.custom.customDomain.rest.apiType = "http"
        this.custom.customDomain.rest.endpointType = "edge"
        this.custom.customDomain.rest.autoDomain = false
      }

      this.custom.defaultCors = {
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
      this.custom.pythonRequirements = {
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
    const inputConfig = this.serverless.configurationInput.provider

    this.providerConfig.deploymentBucket = "kinayu--serverless-deployments"
    this.providerConfig.deploymentBucketObject = {
      name: "kinayu--serverless-deployments",
    }
    if (!inputConfig.runtime) {
      this.providerConfig.runtime = "python3.13"
    }
    if (!inputConfig.memorySize) {
      this.providerConfig.memorySize = 1536
    }
    if (!inputConfig.architecture) {
      this.providerConfig.architecture = "arm64"
    }
    if (!inputConfig.timeout) {
      this.providerConfig.timeout = 20
    }

    this.providerConfig.deploymentMethod = "direct"
    this.providerConfig.versionFunctions = false
    this.providerConfig.logRetentionInDays = 14
    this.providerConfig.environment = this.providerConfig.environment || {}
    this.providerConfig.environment.stage = this.options.stage || "dev"
    this.providerConfig.environment.LOGLEVEL = "DEBUG"
    this.providerConfig.apiGateway = {
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
  }

  setPackageConfig(): void {
    const packageConfig = this.serverless.service.package || {}

    packageConfig.excludeDevDependencies = true
    if (this.custom.tes?.type === "frontend") {
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
    this.serverless.service.functions = this.serverless.service.functions || {}
    const functionConfig = this.serverless.service.functions
    if (!this.custom) {
      throw new Error("Custom config not set")
    }

    if (this.custom.tes?.type === "frontend") {
      functionConfig.cfOriginRequest = {
        handler: ".output/server/index.handler",
        name: `${this.serverless.service.service}-${this.stage}-cfOriginRequest`,
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
        for (const event in functionConfig[functionName].events) {
          for (const key in functionConfig[functionName].events[event]) {
            if (key === "http" || key === "httpApi") {
              functionConfig[functionName].events[event][key].cors =
                this.custom.defaultCors
            }
          }
        }
        /*
        const provisionedConcurrency =
          this.custom.provisionedConcurrency[this.stage] || 0
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
    // Initialize resources structure if it doesn't exist
    this.serverless.service.resources = this.serverless.service.resources || {}
    this.serverless.service.resources.Resources =
      this.serverless.service.resources.Resources || {}
    this.serverless.service.resources.Outputs =
      this.serverless.service.resources.Outputs || {}

    const resourcesConfig = this.serverless.service.resources || {}

    if (this.custom.tes?.type === "frontend") {
      resourcesConfig.Resources = resourcesConfig.Resources || {}
      ;(resourcesConfig.Resources.CloudFrontDistribution = {
        Type: "AWS::CloudFront::Distribution",
        Properties: {
          DistributionConfig: {
            Aliases: [this.custom.aliases[this.stage]],
            Origins: [
              {
                Id: "static",
                DomainName:
                  "frontend--websites.s3-website.eu-central-1.amazonaws.com",
                OriginPath: `/${this.custom.s3bucket}`,
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
                OriginPath: `/${this.stage}`,
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
            Comment: this.custom.s3bucket,
            PriceClass: "PriceClass_100",
            Enabled: true,
            ViewerCertificate: {
              AcmCertificateArn: this.custom.certificate[this.stage],
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
    return this.provider
      .request("CloudFront", "createInvalidation", params)
      .then(
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
  ): Promise<any> | undefined {
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

      return this.provider
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
    if (!this.custom.cloudfrontInvalidate) {
      this.serverless.cli.consoleLog(
        "No CloudFront Invalidation configuration found."
      )
      return
    }

    if (
      !this.custom.cloudfrontInvalidate.distributionId &&
      !this.custom.cloudfrontInvalidate.distributionIdKey
    ) {
      this.serverless.cli.consoleLog(
        "No CloudFront Invalidation configuration found."
      )
      return
    }

    if (!this.custom.cloudfrontInvalidate.autoInvalidate) {
      this.serverless.cli.consoleLog(
        "No CloudFront Invalidation items found. Will skip invalidation."
      )
      return
    }

    return this.invalidateElements([this.custom.cloudfrontInvalidate])
  }

  /*

  // Helper for sequential processing
  async processSequentially<T, U>(
    items: T[],
    fn: (item: T) => Promise<U>
  ): Promise<U[]> {
    const results: U[] = []
    for (const item of items) {
      const result = await fn(item)
      results.push(result)
    }
    return results
  }

  // Match a single glob pattern against a path
  matchPattern(pattern: string, filepath: string): boolean {
    // Convert glob pattern to regex
    const regex = new RegExp(
      `^${pattern
        .split("*")
        .map((s) => s.replace(/[-\/\\^$+?.()|[\]{}]/g, "\\$&"))
        .join(".*")}$`
    )
    return regex.test(filepath)
  }

  // Find files matching glob patterns without external dependencies
  findFiles(pattern: string, options: GlobOptions = {}): string[] {
    const cwd = options.cwd || process.cwd()
    const results: string[] = []

    // Simple glob pattern matching - handles * and directory recursion
    if (pattern.includes("**")) {
      // Handle recursive pattern
      this.traverseDirectory(cwd, "", results, options)

      // Filter results by pattern
      const patternParts = pattern.split("**")
      return results.filter((file) => {
        if (patternParts.length === 2) {
          return (
            file.startsWith(patternParts[0]) && file.endsWith(patternParts[1])
          )
        }
        return this.matchPattern(pattern, file)
      })
    } else if (pattern.includes("*")) {
      // Handle simple wildcard pattern
      this.traverseDirectory(cwd, "", results, options)
      return results.filter((file) => this.matchPattern(pattern, file))
    } else {
      // Direct file or directory
      this.traverseDirectory(cwd, "", results, options)
      return results.filter((file) => file === pattern)
    }
  }

  //Recursively traverse directory and collect files
  traverseDirectory(
    basePath: string,
    relativePath: string,
    results: string[],
    options: GlobOptions
  ): void {
    const currentPath = path.join(basePath, relativePath)
    const entries = fs.readdirSync(currentPath, { withFileTypes: true })

    for (const entry of entries) {
      // Skip hidden files if not including dot files
      if (!options.dot && entry.name.startsWith(".")) {
        continue
      }

      const entryRelativePath = path.join(relativePath, entry.name)

      if (entry.isDirectory()) {
        // If directory, traverse recursively
        this.traverseDirectory(basePath, entryRelativePath, results, options)

        // Add directory to results if not filtering directories
        if (!options.nodir) {
          results.push(entryRelativePath)
        }
      } else if (entry.isFile()) {
        // Add file to results
        results.push(entryRelativePath)
      }
    }
  }

  // Then in your class, update these methods:

  listStackResources(
    resources: StackResource[] = [],
    nextToken?: string
  ): Promise<StackResource[]> {
    if (!this.custom.assets.resolveReferences) {
      return Promise.resolve(resources)
    }

    return this.provider
      .request("CloudFormation", "listStackResources", {
        StackName: this.provider.naming.getStackName(),
        NextToken: nextToken,
      })
      .then(
        (response: {
          StackResourceSummaries: StackResource[]
          NextToken?: string
        }) => {
          resources.push(...response.StackResourceSummaries)
          if (response.NextToken) {
            // Query next page
            return this.listStackResources(resources, response.NextToken)
          }
        }
      )
      .then(() => {
        return resources
      })
  }

  resolveBucket(
    resources: StackResource[],
    value: string | BucketReference
  ): Promise<string> {
    if (typeof value === "string") {
      return Promise.resolve(value)
    } else if (value && value.Ref) {
      let resolved: string | undefined
      resources.forEach((resource) => {
        if (resource && resource.LogicalResourceId === value.Ref) {
          resolved = resource.PhysicalResourceId
        }
      })

      if (!resolved) {
        this.serverless.cli.log(
          `WARNING: Failed to resolve reference ${value.Ref}`
        )
      }
      return Promise.resolve(resolved as string)
    } else {
      return Promise.reject(new Error(`Invalid bucket name ${value}`))
    }
  }

  emptyBucket(bucket: string, dir: string): Promise<void> {
    const listParams = {
      Bucket: bucket,
      Prefix: dir,
    }

    return this.provider
      .request("S3", "listObjectsV2", listParams)
      .then((listedObjects: S3ListObjectsResponse) => {
        if (listedObjects.Contents.length === 0) return

        const deleteParams = {
          Bucket: bucket,
          Delete: { Objects: [] as { Key: string }[] },
        }

        listedObjects.Contents.forEach(({ Key }) => {
          deleteParams.Delete.Objects.push({ Key })
        })

        return this.provider
          .request("S3", "deleteObjects", deleteParams)
          .then(() => {
            if (listedObjects.IsTruncated) {
              this.log("Is not finished. Rerun emptyBucket")
              return this.emptyBucket(bucket, dir)
            }
          })
      })
  }

  deployS3(): Promise<any> {
    const assetSets = this.custom.assets.targets
    const uploadConcurrency = this.custom.assets.uploadConcurrency

    // Read existing stack resources so we can resolve references if necessary
    return this.listStackResources().then((resources) => {
      // Process asset sets in parallel (up to uploadConcurrency)
      return this.mapWithConcurrency(
        assetSets,
        async (assets: AssetSet) => {
          const prefix = assets.prefix || ""
          // Try to resolve the bucket name
          const bucket = await this.resolveBucket(resources, assets.bucket)

          if (this.options.bucket && this.options.bucket !== bucket) {
            this.log(`Skipping bucket: ${bucket}`)
            return ""
          }

          if (assets.empty) {
            this.log(`Emptying bucket: ${bucket}`)
            await this.emptyBucket(bucket, prefix)
          }

          if (!bucket) {
            return
          }

          // Process files serially to not overload the network
          return this.processSequentially(
            assets.files,
            async (opt: AssetFile) => {
              this.log(`Sync bucket: ${bucket}:${prefix}`)
              this.log(`Path: ${opt.source}`)

              const cfg = { nodir: true, cwd: opt.source }
              const filenames = this.findFiles(opt.globs, cfg)
              return this.processSequentially(
                filenames,
                async (filename: string) => {
                  const body = fs.readFileSync(path.join(opt.source, filename))
                  const type =
                    mime.lookup(filename) ||
                    opt.defaultContentType ||
                    "application/octet-stream"

                  this.log(`\tFile:  ${filename} (${type})`)

                  // when using windows path join resolves to backslashes, but s3 is expecting a slash
                  // therefore replace all backslashes with slashes
                  const key = path.join(prefix, filename).replace(/\\/g, "/")

                  const details = Object.assign(
                    {
                      ACL: assets.acl || "private",
                      Body: body,
                      Bucket: bucket,
                      Key: key,
                      ContentType: type,
                    },
                    opt.headers || {}
                  )

                  return this.provider.request("S3", "putObject", details)
                }
              )
            }
          )
        },
        uploadConcurrency
      )
    })
  }
  */
}

// Deno-kompatibler Export
export default ServerlessDefault
