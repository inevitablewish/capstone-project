output "master_public_ip" {
  value = aws_instance.masters[0].public_ip
}
output "worker1_public_ip" {
  value = aws_instance.workers[0].public_ip
}
output "worke2r_public_ip" {
  value = aws_instance.workers[1].public_ip
}