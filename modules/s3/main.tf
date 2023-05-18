resource "aws_s3_bucket" "static" {
  bucket_prefix = "${var.nlp_server_static_bucket}-${var.environment}-"
  force_destroy = true
}

resource "aws_s3_bucket_acl" "static" {
  bucket = aws_s3_bucket.static.id
  acl    = "private"
  depends_on = [ aws_s3_bucket_ownership_controls.s3_bucket_acl_ownership_static ]
}

resource "aws_s3_bucket_ownership_controls" "s3_bucket_acl_ownership_static" {
  bucket = aws_s3_bucket.static.id
  rule {
    object_ownership = "ObjectWriter"
  }
}

resource "aws_s3_bucket" "processed_bucket" {
  bucket_prefix = "${var.s3_bucketname_task_results}-${var.environment}-"
  force_destroy = true
}

resource "aws_s3_bucket_acl" "processed_bucket" {
  bucket = aws_s3_bucket.processed_bucket.id
  acl    = "private"
  depends_on = [ aws_s3_bucket_ownership_controls.s3_bucket_acl_ownership_processed ]
}

resource "aws_s3_bucket_ownership_controls" "s3_bucket_acl_ownership_processed" {
  bucket = aws_s3_bucket.processed_bucket.id
  rule {
    object_ownership = "ObjectWriter"
  }
}